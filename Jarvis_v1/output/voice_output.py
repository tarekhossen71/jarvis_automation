import asyncio
import os
import tempfile
import time

import edge_tts
import pygame


class VoiceOutput:
    """
    Handles text-to-speech output.
    """

    def __init__(self):

        self.enabled = True

        # Natural English voice
        self.voice = "en-US-GuyNeural"

        self.rate = "+0%"
        self.volume = "+0%"
        self.pitch = "+0Hz"

        self.audio_initialized = False

        self._initialize_audio()

    # =========================================================
    # AUDIO INITIALIZATION
    # =========================================================

    def _initialize_audio(self):

        try:

            pygame.mixer.init()

            self.audio_initialized = True

            print("🔊 Voice output initialized.")

        except Exception as e:

            print(
                f"❌ Audio initialization failed: {e}"
            )

    # =========================================================
    # SPEAK
    # =========================================================

    def speak(self, message):

        if not message:
            return

        if not self.enabled:
            return

        print(
            f"🔊 JARVIS: {message}"
        )

        if not self.audio_initialized:

            self._initialize_audio()

        if not self.audio_initialized:
            return

        temp_file = None

        try:

            # -----------------------------------------
            # CREATE TEMP MP3 FILE
            # -----------------------------------------

            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False,
            ) as file:

                temp_file = file.name

            # -----------------------------------------
            # GENERATE VOICE
            # -----------------------------------------

            asyncio.run(
                self._generate_voice(
                    message,
                    temp_file,
                )
            )

            # -----------------------------------------
            # PLAY AUDIO
            # -----------------------------------------

            pygame.mixer.music.load(
                temp_file
            )

            pygame.mixer.music.play()

            # Wait until speech finishes
            while pygame.mixer.music.get_busy():

                time.sleep(0.1)

        except Exception as e:

            print(
                f"❌ Voice output error: {e}"
            )

        finally:

            # Stop current audio
            try:

                pygame.mixer.music.stop()

            except Exception:
                pass

            # Delete temporary MP3
            if temp_file:

                try:

                    if os.path.exists(temp_file):
                        os.remove(temp_file)

                except Exception:
                    pass

    # =========================================================
    # GENERATE VOICE
    # =========================================================

    async def _generate_voice(
        self,
        message,
        file_path,
    ):

        communicate = edge_tts.Communicate(
            text=message,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )

        await communicate.save(
            file_path
        )

    # =========================================================
    # VOICE SETTINGS
    # =========================================================

    def set_voice(self, voice):

        if voice:
            self.voice = voice

    def enable(self):

        self.enabled = True

    def disable(self):

        self.enabled = False

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        try:

            pygame.mixer.music.stop()

        except Exception:
            pass

    # =========================================================
    # CLEANUP
    # =========================================================

    def cleanup(self):

        try:

            pygame.mixer.quit()

        except Exception:
            pass