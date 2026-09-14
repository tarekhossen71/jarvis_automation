from input.text_input import TextInput
from input.voice_input import VoiceInput


class InputManager:

    TEXT_MODE = "text"
    VOICE_MODE = "voice"

    MODE_COMMANDS = {
        "switch to voice mode": VOICE_MODE,
        "voice mode": VOICE_MODE,
        "enable voice mode": VOICE_MODE,

        "switch to text mode": TEXT_MODE,
        "text mode": TEXT_MODE,
        "enable text mode": TEXT_MODE,
    }

    def __init__(
        self,
        initial_mode="text",
        voice_language="en-US",
    ):

        self.text_input = TextInput()

        self.voice_input = VoiceInput(
            language=voice_language,
        )

        initial_mode = str(
            initial_mode
        ).lower().strip()

        if initial_mode not in (
            self.TEXT_MODE,
            self.VOICE_MODE,
        ):
            initial_mode = self.TEXT_MODE

        self.mode = initial_mode

        # Voice mode always starts in standby.
        if self.mode == self.VOICE_MODE:
            self.voice_input.standby()

    # =========================================================
    # MODE
    # =========================================================

    def get_mode(self):
        return self.mode

    # =========================================================
    # SET MODE
    # =========================================================

    def set_mode(self, mode):

        mode = str(mode).lower().strip()

        if mode not in (
            self.TEXT_MODE,
            self.VOICE_MODE,
        ):
            return False

        # ---------------------------------------------
        # ALREADY IN SAME MODE
        # ---------------------------------------------

        if mode == self.mode:

            # If already in voice mode, keep standby.
            if mode == self.VOICE_MODE:
                self.voice_input.standby()

            return True

        # ---------------------------------------------
        # SWITCH TO VOICE
        # ---------------------------------------------

        if mode == self.VOICE_MODE:

            self.mode = self.VOICE_MODE

            # IMPORTANT:
            # Do NOT activate continuous conversation yet.
            # First wait for "Hey Jarvis".

            self.voice_input.standby()

            print()
            print("🎤 Voice mode active.")
            print("🎤 JARVIS is in standby.")
            print("🎤 Say 'Hey Jarvis' to start conversation.")

            return True

        # ---------------------------------------------
        # SWITCH TO TEXT
        # ---------------------------------------------

        if mode == self.TEXT_MODE:

            self.voice_input.standby()

            self.mode = self.TEXT_MODE

            print()
            print("⌨️ Text mode active.")

            return True

        return False

    # =========================================================
    # MODE COMMAND
    # =========================================================

    def detect_mode_command(self, text):

        if not text:
            return None

        normalized = text.lower().strip()

        return self.MODE_COMMANDS.get(
            normalized
        )

    # =========================================================
    # HANDLE MODE COMMAND
    # =========================================================

    def handle_mode_command(self, text):

        new_mode = self.detect_mode_command(text)

        if not new_mode:
            return False

        self.set_mode(new_mode)

        return True

    # =========================================================
    # TEXT INPUT
    # =========================================================

    def get_text_input(self):

        text = self.text_input.get_input()

        if text == "__EXIT__":
            return "__EXIT__"

        if not text:
            return None

        # ---------------------------------------------
        # MODE SWITCH
        # ---------------------------------------------

        if self.handle_mode_command(text):

            if self.mode == self.VOICE_MODE:
                return "__VOICE_MODE__"

            return "__TEXT_MODE__"

        return text

    # =========================================================
    # VOICE INPUT
    # =========================================================

    def get_voice_input(self):

        # ---------------------------------------------
        # STANDBY
        # ---------------------------------------------

        if not self.voice_input.is_active():

            command = self.voice_input.wait_for_wake_word()

            if command is None:
                return None

            # -----------------------------------------
            # COMMAND SPOKEN WITH WAKE WORD
            #
            # Example:
            # "Hey Jarvis open Chrome"
            # -----------------------------------------

            if command:

                # Check mode switch first.
                if self.handle_mode_command(command):

                    if self.mode == self.TEXT_MODE:
                        return "__TEXT_MODE__"

                    return "__VOICE_MODE__"

                # Wake word + normal command.
                # Automatically enter continuous conversation.
                self.voice_input.activate()

                return command

            # User only said:
            #
            # "Hey Jarvis"
            #
            # Now activate conversation.
            self.voice_input.activate()

            return None

        # ---------------------------------------------
        # CONTINUOUS CONVERSATION
        # ---------------------------------------------

        command = self.voice_input.listen_for_command()

        if command == "__STANDBY__":

            return "__STANDBY__"

        if not command:
            return None

        # ---------------------------------------------
        # MODE SWITCH
        # ---------------------------------------------

        if self.handle_mode_command(command):

            if self.mode == self.TEXT_MODE:
                return "__TEXT_MODE__"

            return "__VOICE_MODE__"

        return command

    # =========================================================
    # MAIN INPUT
    # =========================================================

    def get_input(self):

        if self.mode == self.TEXT_MODE:

            return self.get_text_input()

        if self.mode == self.VOICE_MODE:

            return self.get_voice_input()

        return None

    # =========================================================
    # VOICE STANDBY
    # =========================================================

    def standby_voice(self):

        self.voice_input.standby()

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.voice_input.stop()