
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
        gemini_tools = self.tools.get_functions()

        # ==========================================
        # RATE LIMIT
        # ==========================================

        self.min_request_interval = 15

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

        elapsed = time.time() - self.last_request_time

        if elapsed < self.min_request_interval:

            wait_time = (
                self.min_request_interval - elapsed
            )

            print(
                f"⏳ Gemini rate limit protection: "
                f"waiting {wait_time:.1f}s..."
            )

            time.sleep(wait_time)

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

                response_text = response.text.strip()

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

                    return (
                        "Gemini is temporarily rate-limited. "
                        f"Please try again after "
                        f"{retry_seconds} seconds."
                    )

                return (
                    "Gemini error: "
                    f"{error_text}"
                )

        return "Gemini is temporarily unavailable."

    # ==================================================
    # PROCESS
    # ==================================================

    def process(self, user_input):

        if not user_input:
            return None

        return self.ask_ai(
            user_input
        )

