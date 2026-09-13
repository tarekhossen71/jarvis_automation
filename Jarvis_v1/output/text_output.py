class TextOutput:
    """
    Handles text responses.
    """

    def send(self, message):
        if message is None:
            return

        print(f"🤖 JARVIS: {message}")