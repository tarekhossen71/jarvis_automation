class TextInput:
    """
    Handles keyboard/text input.
    """

    def get_input(self):
        try:
            user_input = input("👤 You: ").strip()

            if not user_input:
                return None

            return user_input

        except (KeyboardInterrupt, EOFError):
            return "exit"