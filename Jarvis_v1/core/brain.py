
import time
import re

from google import genai

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    SYSTEM_PROMPT,
)


from tools.registry import ToolRegistry
from tools.tool_register import register_all_tools
from tools.clipboard.clipboard_manager import start_clipboard_monitor
from tools.reminders.reminder_manager import (
    start_reminder_monitor,
)

from core.memory import MemoryManager
from core.context import ContextManager
from core.offline_brain import OfflineBrain

class Brain:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing from .env"
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        self.model = MODEL_NAME

        # ==========================================
        # MEMORY + CONTEXT
        # ==========================================

        self.memory = MemoryManager()

        self.context = ContextManager(
            memory_manager=self.memory,
            max_messages=10,
        )

        # Offline fallback brain using Ollama
        self.offline_brain = OfflineBrain()

        

        # ==========================================
        # TOOLS
        # ==========================================

        self.tools = ToolRegistry()

        # Register tools using the separate module
        register_all_tools(self.tools)

        # Start clipboard monitoring
        start_clipboard_monitor()

        # Start background reminder monitor
        start_reminder_monitor()

        # Get all registered tools dynamically
        # gemini_tools = self.tools.get_functions()
        gemini_tools = []

        # ==========================================
        # RATE LIMIT
        # ==========================================

        self.min_request_interval = 0

        self.last_request_time = 0

        # ==========================================
        # GEMINI CHAT
        # ==========================================

        self.chat = self.client.chats.create(
            model=self.model,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "tools": gemini_tools,
            },
        )

    # ==================================================
    # WAIT BEFORE REQUEST
    # ==================================================

    def wait_for_rate_limit(self):

        # elapsed = time.time() - self.last_request_time

        # if elapsed < self.min_request_interval:

        #     wait_time = (
        #         self.min_request_interval - elapsed
        #     )

        #     print(
        #         f"⏳ Gemini rate limit protection: "
        #         f"waiting {wait_time:.1f}s..."
        #     )

        #     time.sleep(wait_time)
        return

    # ==================================================
    # EXTRACT RETRY TIME FROM GEMINI ERROR
    # ==================================================

    def get_retry_seconds(self, error):

        error_text = str(error)

        match = re.search(
            r"(?:retry in|retryDelay[^\d]*)(\d+(?:\.\d+)?)\s*s",
            error_text,
            re.IGNORECASE,
        )

        if match:

            return max(
                1,
                int(float(match.group(1))) + 1
            )

        return 60

    # ==================================================
    # ASK AI
    # ==================================================

    def ask_ai(self, user_input):

        max_retries = 2

        for attempt in range(max_retries):

            try:

                self.wait_for_rate_limit()

                print(
                    "🧠 Gemini: processing..."
                )

                # ======================================
                # BUILD CONTEXT
                # ======================================

                context = self.context.get_context()

                prompt = f"""
                    {context}

                    CURRENT USER MESSAGE:
                    {user_input}
                    """

                # ======================================
                # SEND TO GEMINI
                # ======================================

                response = self.chat.send_message(
                    prompt
                )

                self.last_request_time = time.time()

                response_text = (
                    response.text.strip()
                    if response.text
                    else ""
                )

                # ======================================
                # EMPTY RESPONSE PROTECTION
                # ======================================

                if not response_text:

                    if attempt < max_retries - 1:

                        print(
                            "⚠️ Gemini returned an empty response. "
                            "Retrying..."
                        )

                        time.sleep(2)

                        continue

                    return (
                        "I received an empty response from Gemini. "
                        "Please try again."
                    )

                # ======================================
                # SAVE CONVERSATION
                # ======================================

                self.context.save_user_message(
                    user_input
                )

                self.context.save_assistant_message(
                    response_text
                )

                return response_text

            except Exception as e:

                error_text = str(e)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    retry_seconds = self.get_retry_seconds(
                        e
                    )

                    if attempt < max_retries - 1:

                        print(
                            "⚠️ Gemini quota/rate limit reached."
                        )

                        print(
                            f"⏳ Retrying in "
                            f"{retry_seconds}s..."
                        )

                        time.sleep(
                            retry_seconds
                        )

                        continue

                    print(
                        "🧠 Gemini is rate-limited."
                    )

                    print(
                        "🧠 Switching to OfflineBrain..."
                    )

                    offline_response = (
                        self.offline_brain.process(
                            user_input=user_input,
                            context=self.context.get_context(),
                        )
                    )

                    if offline_response:
                        self.context.save_user_message(
                            user_input
                        )

                        self.context.save_assistant_message(
                            offline_response
                        )

                        return offline_response

                    return (
                        "Gemini is temporarily rate-limited "
                        "and the offline brain is unavailable."
                    )

                print(
                    f"⚠️ Gemini error: {error_text}"
                )

                print(
                    "🧠 Switching to OfflineBrain..."
                )

                offline_response = (
                    self.offline_brain.process(
                        user_input=user_input,
                        context=self.context.get_context(),
                    )
                )

                if offline_response:
                    self.context.save_user_message(
                        user_input
                    )

                    self.context.save_assistant_message(
                        offline_response
                    )

                    return offline_response

                return (
                    "Gemini is unavailable and "
                    "the offline brain could not respond."
                )

        return "Gemini is temporarily unavailable."

        # ==================================================
    # PROCESS
    # ==================================================

    def process_tool_results(
        self,
        user_input,
        tool_results,
    ):
        """
        Convert real tool results into a natural
        JARVIS response using the existing Gemini chat.

        Includes:
        - Gemini retry for temporary 503 errors
        - Safe fallback if Gemini remains unavailable
        """

        if not tool_results:
            return "I could not get any tool results."

        prompt = f"""
                The user asked:

                {user_input}

                I executed the required JARVIS tools.

                REAL TOOL RESULTS:

                {tool_results}

                Now answer the user's original question.

                Rules:

                1. Use ONLY the information in the tool results.
                2. Never invent values.
                3. Never claim a tool failed if it succeeded.
                4. Clearly provide the actual result to the user.
                5. If the result contains RAM information, mention the
                current RAM usage and useful RAM values.
                6. If the result contains CPU information, mention CPU usage.
                7. If the result contains disk information, mention disk usage.
                8. If the result contains battery information, mention battery.
                9. For application/file/browser actions, clearly tell the
                user what was completed.
                10. Keep the answer concise and natural.
                11. Reply in English or Banglish only.
                12. Do not mention internal tool names unless necessary.
                13. Do not say "I executed a tool".
                """

        # ==================================================
        # TRY GEMINI
        # ==================================================

        max_attempts = 2

        for attempt in range(max_attempts):

            try:
                self.wait_for_rate_limit()

                response = self.chat.send_message(
                    prompt
                )

                response_text = (
                    response.text.strip()
                    if response.text
                    else ""
                )

                if response_text:

                    self.last_request_time = time.time()

                    self.context.save_user_message(
                        user_input
                    )

                    self.context.save_assistant_message(
                        response_text
                    )

                    return response_text

                print("⚠️ Gemini returned an empty final response.")

            except Exception as e:

                error_text = str(e).lower()

                # Temporary Gemini availability problem
                is_temporary_error = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "high demand" in error_text
                    or "resource_exhausted" in error_text
                    or "429" in error_text
                )

                if (
                    is_temporary_error
                    and attempt < max_attempts - 1
                ):

                    time.sleep(3)

                    continue

                # ==================================================
                # FALLBACK
                # ==================================================

                fallback_response = (
                    self._build_tool_result_fallback(
                        user_input=user_input,
                        tool_results=tool_results,
                    )
                )

                self.context.save_user_message(
                    user_input
                )

                self.context.save_assistant_message(
                    fallback_response
                )

                return fallback_response

        # Safety fallback
        fallback_response = (
            self._build_tool_result_fallback(
                user_input=user_input,
                tool_results=tool_results,
            )
        )

        self.context.save_user_message(
            user_input
        )

        self.context.save_assistant_message(
            fallback_response
        )

        return fallback_response


    # ==================================================
    # TOOL RESULT FALLBACK
    # ==================================================

    def _build_tool_result_fallback(
        self,
        user_input,
        tool_results,
    ):
        """
        Build a natural user-friendly response directly
        from real tool results when Gemini is unavailable.
        """

        messages = []

        for item in tool_results:

            if not isinstance(item, dict):
                continue

            success = item.get("success", False)
            action = item.get("action", "")
            result = item.get("result")
            error = item.get("error")

            # ==================================================
            # SUCCESS
            # ==================================================

            if success:

                # --------------------------------------------------
                # APPLICATION
                # --------------------------------------------------

                if action == "open_application":

                    if isinstance(result, dict):

                        application = result.get(
                            "application",
                            result.get(
                                "app_name",
                                "application"
                            )
                        )

                        messages.append(
                            f"Done. I opened {application}."
                        )

                    else:

                        messages.append(
                            "Done. I opened the application."
                        )

                # --------------------------------------------------
                # BROWSER / URL
                # --------------------------------------------------

                elif action in (
                    "open_url",
                    "open_website",
                    "google_search",
                    "youtube_search",
                    "play_youtube",
                ):

                    if isinstance(result, dict):

                        browser = result.get(
                            "browser"
                        )

                        url = result.get(
                            "url"
                        )

                        if action in (
                            "google_search",
                            "youtube_search",
                        ):

                            if browser:

                                messages.append(
                                    f"Done. I searched using {browser}."
                                )

                            else:

                                messages.append(
                                    "Done. I completed the search."
                                )

                        elif url:

                            messages.append(
                                f"Done. I opened the requested page."
                            )

                        else:

                            messages.append(
                                "Done. I completed the browser action."
                            )

                    else:

                        messages.append(
                            "Done. I completed the browser action."
                        )

                # --------------------------------------------------
                # RAM
                # --------------------------------------------------

                elif isinstance(result, dict) and (
                    "ram_usage_percent" in result
                ):

                    usage = result.get(
                        "ram_usage_percent"
                    )

                    total = result.get(
                        "total_gb"
                    )

                    available = result.get(
                        "available_gb"
                    )

                    messages.append(
                        f"RAM usage is {usage}%. "
                        f"Total RAM: {total} GB. "
                        f"Available RAM: {available} GB."
                    )

                # --------------------------------------------------
                # CPU
                # --------------------------------------------------

                elif isinstance(result, dict) and (
                    "cpu_usage_percent" in result
                ):

                    usage = result.get(
                        "cpu_usage_percent"
                    )

                    messages.append(
                        f"Current CPU usage is {usage}%."
                    )

                # --------------------------------------------------
                # BATTERY
                # --------------------------------------------------

                elif isinstance(result, dict) and (
                    "percent" in result
                    and (
                        "plugged" in result
                        or "power_plugged" in result
                    )
                ):

                    percent = result.get(
                        "percent"
                    )

                    plugged = result.get(
                        "plugged",
                        result.get(
                            "power_plugged"
                        )
                    )

                    if plugged:

                        messages.append(
                            f"Battery is at {percent}% "
                            f"and the charger is connected."
                        )

                    else:

                        messages.append(
                            f"Battery is at {percent}% "
                            f"and the charger is not connected."
                        )

                # --------------------------------------------------
                # DISK
                # --------------------------------------------------

                elif isinstance(result, dict) and (
                    "free_gb" in result
                    and "total_gb" in result
                ):

                    drive = result.get(
                        "drive",
                        ""
                    )

                    free_gb = result.get(
                        "free_gb"
                    )

                    total_gb = result.get(
                        "total_gb"
                    )

                    used_gb = result.get(
                        "used_gb"
                    )

                    usage = result.get(
                        "usage_percent"
                    )

                    messages.append(
                        f"You have {free_gb} GB of free "
                        f"space on the {drive} drive. "
                        f"It is using {used_gb} GB out of "
                        f"{total_gb} GB ({usage}% used)."
                    )

                # --------------------------------------------------
                # WEB RESEARCH
                # --------------------------------------------------

                elif isinstance(result, dict) and (
                    "results" in result
                ):

                    research_results = result.get(
                        "results"
                    )

                    if isinstance(
                        research_results,
                        list
                    ):

                        if not research_results:

                            messages.append(
                                "I could not find any relevant results."
                            )

                        else:

                            messages.append(
                                f"I found {len(research_results)} relevant result(s)."
                            )

                            for index, research_item in enumerate(
                                research_results[:5],
                                start=1
                            ):

                                if not isinstance(
                                    research_item,
                                    dict
                                ):
                                    continue

                                title = research_item.get(
                                    "title"
                                )

                                url = research_item.get(
                                    "url"
                                )

                                if title and url:

                                    messages.append(
                                        f"{index}. {title} - {url}"
                                    )

                                elif title:

                                    messages.append(
                                        f"{index}. {title}"
                                    )

                # --------------------------------------------------
                # GENERIC SUCCESS
                # --------------------------------------------------

                else:

                    messages.append(
                        "Done. I completed the requested action."
                    )

            # ==================================================
            # FAILURE
            # ==================================================

            elif error:

                messages.append(
                    f"I could not complete that action: {error}"
                )

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        if messages:

            return "\n".join(messages)

        return (
            "The requested action was completed, "
            "but I could not generate a detailed response."
        )



    def process(self, user_input):
    
        if not user_input:
            return None

        return self.ask_ai(
            user_input
        )