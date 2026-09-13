class VoiceOutput:
    """
    Handles text-to-speech output.
    """

    def __init__(self):
        self.enabled = True

    def speak(self, message):

        if not message:
            return

        print(f"🔊 JARVIS: {message}")

        # Actual TTS engine will be connected here.