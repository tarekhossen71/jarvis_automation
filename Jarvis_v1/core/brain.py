
import time
import re

from google import genai

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    SYSTEM_PROMPT,
)

from tools.registry import ToolRegistry
from tools.system.system_info import get_system_info


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

        self.tools = ToolRegistry()

        self.register_tools()

        # Get all registered tools dynamically
        gemini_tools = self.tools.get_functions()

        # Minimum gap between Gemini requests.
        # This helps avoid Free Tier RPM errors.
        self.min_request_interval = 15

        self.last_request_time = 0

        # Gemini automatic function calling
        self.chat = self.client.chats.create(
            model=self.model,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "tools": gemini_tools,
            },
        )

    # ==================================================
    # REGISTER TOOLS
    # ==================================================

    def register_tools(self):

        self.tools.register(
            name="get_system_info",
            description=(
                "Get the current computer system information. "
                "Use this tool whenever the user asks about "
                "RAM usage, CPU usage, disk usage, operating "
                "system, computer information, or system status."
            ),
            function=get_system_info,
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

        # Example:
        # retryDelay: 58s
        # retry in 58.138098759s

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

        # Safe fallback
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

                response = self.chat.send_message(
                    user_input
                )

                self.last_request_time = time.time()

                return response.text.strip()

            except Exception as e:

                error_text = str(e)

                # Gemini 429 / RESOURCE_EXHAUSTED
                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    retry_seconds = self.get_retry_seconds(
                        e
                    )

                    if attempt < max_retries - 1:

                        print(
                            f"⚠️ Gemini quota/rate limit reached."
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

                # Other Gemini error
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

        return self.ask_ai(user_input)
