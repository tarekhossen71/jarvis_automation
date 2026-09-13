from config import INPUT_MODE

from input.text_input import TextInput
from input.voice_input import VoiceInput


class InputManager:

    def __init__(self):
        self.mode = INPUT_MODE

        self.text_input = TextInput()
        self.voice_input = VoiceInput()

    def set_mode(self, mode):
        mode = mode.lower().strip()

        allowed_modes = [
            "text",
            "voice",
            "hybrid",
        ]

        if mode not in allowed_modes:
            raise ValueError(
                f"Invalid input mode: {mode}"
            )

        self.mode = mode

        if mode != "voice":
            self.voice_input.stop()

        print(f"🔄 Input mode: {self.mode}")

    def get_input(self):

        # ==========================================
        # TEXT
        # ==========================================

        if self.mode == "text":
            return self.text_input.get_input()


        # ==========================================
        # VOICE
        # ==========================================

        if self.mode == "voice":
            return self.voice_input.get_input()


        # ==========================================
        # HYBRID
        # ==========================================

        if self.mode == "hybrid":

            # Temporary behavior:
            # Hybrid input will later support
            # simultaneous voice + keyboard.

            return self.text_input.get_input()


        return None