from config import OUTPUT_MODE

from output.text_output import TextOutput
from output.voice_output import VoiceOutput


class OutputManager:

    def __init__(self):

        self.mode = OUTPUT_MODE

        self.text_output = TextOutput()
        self.voice_output = VoiceOutput()

    # =========================================================
    # SET MODE
    # =========================================================

    def set_mode(self, mode):

        mode = mode.lower().strip()

        allowed_modes = [
            "text",
            "voice",
            "auto",
        ]

        if mode not in allowed_modes:
            raise ValueError(
                f"Invalid output mode: {mode}"
            )

        self.mode = mode

    # =========================================================
    # SEND
    # =========================================================

    def send(self, message, input_mode=None):

        if not message:
            return

        # TEXT OUTPUT
        if self.mode == "text":

            self.text_output.send(message)
            return

        # VOICE OUTPUT
        if self.mode == "voice":

            self.voice_output.speak(message)
            return

        # AUTO MODE
        if self.mode == "auto":

            if input_mode == "voice":

                self.voice_output.speak(message)

            else:

                self.text_output.send(message)