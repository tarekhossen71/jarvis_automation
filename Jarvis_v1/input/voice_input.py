class VoiceInput:
    """
    Handles microphone/voice input.

    Actual speech recognition engine will be connected here.
    """

    def __init__(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_input(self):
        """
        Returns recognized speech as text.
        """

        if not self.running:
            self.start()

        print("🎤 Listening...")

        # Voice engine will be connected here.
        return None