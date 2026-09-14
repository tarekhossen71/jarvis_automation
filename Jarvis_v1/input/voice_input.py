import re
import speech_recognition as sr


class VoiceInput:
    """
    JARVIS Voice Input

    Behavior:
    - Standby mode
    - Wake word: "Hey Jarvis" / "Jarvis"
    - Continuous conversation after wake
    - Stop listening -> standby
    - No need to say wake word before every command
    """

    WAKE_WORDS = (
        "hey jarvis",
        "jarvis",
    )

    STOP_COMMANDS = (
        "stop listening",
        "go to standby",
        "standby",
        "stop listening jarvis",
    )

    def __init__(
        self,
        language="en-US",
        timeout=5,
        phrase_time_limit=8,
    ):
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

        self.recognizer = sr.Recognizer()

        self.active = False
        self.running = True

        self.microphone = None

        self._initialize_microphone()

    # ---------------------------------------------------------
    # MICROPHONE
    # ---------------------------------------------------------

    def _initialize_microphone(self):
        try:
            self.microphone = sr.Microphone()

        except Exception as e:
            print(f"Voice microphone initialization failed: {e}")
            self.microphone = None

    # ---------------------------------------------------------
    # CALIBRATION
    # ---------------------------------------------------------

    def calibrate(self):
        if not self.microphone:
            return False

        try:
            print("Calibrating microphone...")

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1,
                )

            print("Microphone ready.")

            return True

        except Exception as e:
            print(f"Microphone calibration failed: {e}")
            return False

    # ---------------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------------

    @staticmethod
    def normalize(text):
        if not text:
            return ""

        text = text.lower().strip()

        text = re.sub(r"\s+", " ", text)

        return text

    # ---------------------------------------------------------
    # WAKE WORD
    # ---------------------------------------------------------

    def contains_wake_word(self, text):
        text = self.normalize(text)

        for wake_word in self.WAKE_WORDS:
            if wake_word in text:
                return True

        return False

    # ---------------------------------------------------------
    # REMOVE WAKE WORD
    # ---------------------------------------------------------

    def remove_wake_word(self, text):
        text = self.normalize(text)

        for wake_word in self.WAKE_WORDS:
            text = text.replace(wake_word, "")

        return text.strip()

    # ---------------------------------------------------------
    # STOP COMMAND
    # ---------------------------------------------------------

    def is_stop_command(self, text):
        text = self.normalize(text)

        return text in self.STOP_COMMANDS

    # ---------------------------------------------------------
    # LISTEN ONCE
    # ---------------------------------------------------------

    def listen_once(self):
        if not self.microphone:
            return ""

        try:
            with self.microphone as source:

                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )

            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
            )

            return text.strip()

        except sr.WaitTimeoutError:
            return ""

        except sr.UnknownValueError:
            return ""

        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return ""

        except OSError as e:
            print(f"Microphone error: {e}")
            return ""

        except Exception as e:
            print(f"Voice input error: {e}")
            return ""

    # ---------------------------------------------------------
    # WAIT FOR WAKE WORD
    # ---------------------------------------------------------

    def wait_for_wake_word(self):
        """
        Standby mode.

        Keeps listening until Jarvis wake word is detected.

        Returns:
            None
            OR command spoken together with wake word.

        Example:
            "Hey Jarvis open Chrome"

        returns:

            "open Chrome"
        """

        self.active = False

        while self.running:

            text = self.listen_once()

            if not text:
                continue

            if not self.contains_wake_word(text):
                continue

            self.active = True

            command = self.remove_wake_word(text)

            return command or None

        return None

    # ---------------------------------------------------------
    # CONTINUOUS COMMAND
    # ---------------------------------------------------------

    def listen_for_command(self):
        """
        Called while conversation mode is active.
        """

        if not self.active:
            return None

        text = self.listen_once()

        if not text:
            return None

        if self.is_stop_command(text):

            self.active = False

            return "__STANDBY__"

        return text

    # ---------------------------------------------------------
    # ACTIVATE
    # ---------------------------------------------------------

    def activate(self):
        self.active = True

    # ---------------------------------------------------------
    # STANDBY
    # ---------------------------------------------------------

    def standby(self):
        self.active = False

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def is_active(self):
        return self.active

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop(self):
        self.running = False
        self.active = False