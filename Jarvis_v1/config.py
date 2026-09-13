import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# JARVIS MODE
# =========================================================

# text  = keyboard input
# voice = microphone input
# hybrid = text + voice
INPUT_MODE = os.getenv("INPUT_MODE", "text").lower()

# auto   = input mode অনুযায়ী output
# text   = always print text
# voice  = always speak
OUTPUT_MODE = os.getenv("OUTPUT_MODE", "auto").lower()


# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gemini-3.6-flash"
)


# =========================================================
# JARVIS
# =========================================================

ASSISTANT_NAME = "JARVIS"
USER_NAME = "Tarek"


# =========================================================
# VOICE
# =========================================================

VOICE_LANGUAGE = os.getenv(
    "VOICE_LANGUAGE",
    "en-US"
)

WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "জারভিস",
]

SYSTEM_PROMPT = """
You are JARVIS, a helpful AI assistant.

LANGUAGE RULE:
- Never reply using Bengali/Bangla Unicode script.
- Reply only in English or Banglish (Romanized Bengali).
- If the user writes in Banglish, prefer Banglish.
- If the user writes in English, reply in English.
- Never use Bengali Unicode characters.
"""

# =========================================================
# DEBUG
# =========================================================

DEBUG = os.getenv("DEBUG", "true").lower() == "true"