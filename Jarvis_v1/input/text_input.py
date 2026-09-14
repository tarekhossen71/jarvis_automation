class TextInput:

    def get_input(self):
        try:
            text = input("👤 You: ")

            return text.strip()

        except (KeyboardInterrupt, EOFError):
            return "__EXIT__"