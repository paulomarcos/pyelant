"""
Python Easy Language Translator.

Translates text from the command line, the clipboard or the microphone and
places the result on the clipboard.
"""

import asyncio
import sys
import threading

import pyperclip
from googletrans import LANGCODES, LANGUAGES, Translator

APP_NAME = "pyelant"
CLIPBOARD_HOTKEY = "<ctrl>+<alt>+e"
MICROPHONE_HOTKEY = "<ctrl>+<alt>+m"


def normalize_language(language, allow_auto=False):
    """Return the language code for a code or name such as "ja" or "Japanese".

    Raises ValueError if the language is not supported.
    """
    language = language.strip().lower()
    if allow_auto and language == "auto":
        return language
    if language in LANGUAGES:
        return language
    if language in LANGCODES:
        return LANGCODES[language]
    raise ValueError(f"unsupported language: {language!r}")


class PyElant:
    """Translates text and copies the result to the clipboard."""

    def __init__(self, input_language="en", output_language="ja",
                 notifications=True, verbose=False):
        self.input_language = input_language
        self.output_language = output_language
        self.notifications = notifications
        self.verbose = verbose
        self._notifier = None
        self._busy = threading.Lock()

    def translate(self, text):
        """Return the translation of text."""
        return asyncio.run(self._translate(text))

    async def _translate(self, text):
        async with Translator() as translator:
            result = await translator.translate(text,
                                                src=self.input_language,
                                                dest=self.output_language)
        return result.text

    def translate_to_clipboard(self, text):
        """Translate text, copy the result to the clipboard and return it."""
        translation = self.translate(text)
        self.log(f"Input: {text}")
        self.log(f"Output: {translation}")
        pyperclip.copy(translation)
        self.notify(text, f"{translation} was copied to the clipboard")
        return translation

    def translate_clipboard(self):
        """Translate the text currently in the clipboard back into it."""
        text = pyperclip.paste()
        if not text.strip():
            self.log("Clipboard is empty")
            return
        self.translate_to_clipboard(text)

    def translate_speech(self):
        """Listen to the microphone and translate what was said."""
        try:
            import pyaudio  # noqa: F401  (required by speech_recognition.Microphone)
            import speech_recognition as sr
        except ImportError:
            print('Microphone support is not installed. Run: pip install "pyelant[mic]"',
                  file=sys.stderr)
            return
        if self.input_language == "auto":
            print("Microphone input needs an explicit input language, e.g. -i en",
                  file=sys.stderr)
            return

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.log("Say something")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language=self.input_language)
        except sr.UnknownValueError:
            self.log("Speech Recognition could not understand audio")
            return
        except sr.RequestError as error:
            print(f"Could not request results from Speech Recognition service: {error}",
                  file=sys.stderr)
            return
        self.translate_to_clipboard(text)

    def run(self):
        """Wait for hotkeys in the background until interrupted with Ctrl+C."""
        # Imported here so that one-off translations work without a display server.
        from pynput import keyboard

        hotkeys = {
            CLIPBOARD_HOTKEY: lambda: self._start_job(self.translate_clipboard),
            MICROPHONE_HOTKEY: lambda: self._start_job(self.translate_speech),
        }
        print(f"PyElant is running ({self.input_language} -> {self.output_language}). "
              "Ctrl+Alt+E translates the clipboard, Ctrl+Alt+M listens to the microphone. "
              "Press Ctrl+C to quit.")
        with keyboard.GlobalHotKeys(hotkeys) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                listener.stop()

    def _start_job(self, job):
        """Run job in a worker thread so the key listener is never blocked."""
        if not self._busy.acquire(blocking=False):
            self.log("A translation is already in progress")
            return
        threading.Thread(target=self._run_job, args=(job,), daemon=True).start()

    def _run_job(self, job):
        try:
            job()
        except Exception as error:  # noqa: BLE001
            # Keep the background listener alive whatever goes wrong.
            print(f"Translation failed: {error}", file=sys.stderr)
        finally:
            self._busy.release()

    def notify(self, title, message):
        """Show a desktop notification, if enabled and supported."""
        if not self.notifications:
            return
        try:
            if self._notifier is None:
                from desktop_notifier import DesktopNotifierSync
                self._notifier = DesktopNotifierSync(app_name=APP_NAME)
            self._notifier.send(title=title, message=message)
        except Exception as error:  # noqa: BLE001
            # Notifications are a nicety; never let them break a translation.
            self.log(f"Could not show notification: {error}")

    def log(self, message):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)
