"""Tests for the background mode: hotkeys, microphone input and notifications."""

import sys
import types
from typing import ClassVar

import pytest

from pyelant import pyelant as core

from .conftest import FakeTranslator


def wait_for_job(pyelant):
    """Block until the worker thread started by a hotkey has finished."""
    assert pyelant._busy.acquire(timeout=5), "background job did not finish"
    pyelant._busy.release()


# Microphone ---------------------------------------------------------------------------

@pytest.fixture
def fake_speech(monkeypatch):
    """Install fake speech_recognition and pyaudio modules."""
    sr = types.ModuleType("speech_recognition")

    class UnknownValueError(Exception):
        pass

    class RequestError(Exception):
        pass

    class Microphone:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class Recognizer:
        result = "Hello"
        languages: ClassVar[list] = []

        def listen(self, source):
            return "audio"

        def recognize_google(self, audio, language):
            Recognizer.languages.append(language)
            if isinstance(Recognizer.result, Exception):
                raise Recognizer.result
            return Recognizer.result

    sr.UnknownValueError = UnknownValueError
    sr.RequestError = RequestError
    sr.Microphone = Microphone
    sr.Recognizer = Recognizer
    monkeypatch.setitem(sys.modules, "speech_recognition", sr)
    monkeypatch.setitem(sys.modules, "pyaudio", types.ModuleType("pyaudio"))
    return sr


def test_translate_speech(fake_speech, fakes):
    core.PyElant("en", "ja", notifications=False).translate_speech()
    assert fake_speech.Recognizer.languages == ["en"]
    assert fakes["value"] == "[ja] Hello"


def test_translate_speech_not_understood(fake_speech, fakes):
    fake_speech.Recognizer.result = fake_speech.UnknownValueError()
    core.PyElant(notifications=False).translate_speech()
    assert FakeTranslator.calls == []
    assert fakes["value"] == ""


def test_translate_speech_service_error(fake_speech, capsys):
    fake_speech.Recognizer.result = fake_speech.RequestError("quota exceeded")
    core.PyElant(notifications=False).translate_speech()
    assert "quota exceeded" in capsys.readouterr().err
    assert FakeTranslator.calls == []


def test_translate_speech_rejects_auto_language(fake_speech, capsys):
    core.PyElant("auto", "ja", notifications=False).translate_speech()
    assert "explicit input language" in capsys.readouterr().err
    assert fake_speech.Recognizer.languages == []


@pytest.mark.parametrize("missing", ["pyaudio", "speech_recognition"])
def test_translate_speech_without_mic_extra(fake_speech, monkeypatch, capsys, missing):
    monkeypatch.setitem(sys.modules, missing, None)  # makes the import raise ImportError
    core.PyElant(notifications=False).translate_speech()
    assert 'pip install "pyelant[mic]"' in capsys.readouterr().err


# Hotkeys ------------------------------------------------------------------------------

@pytest.fixture
def fake_pynput(monkeypatch):
    """Install a fake pynput whose listener fires the given hotkeys, then gets Ctrl+C."""
    keyboard = types.ModuleType("pynput.keyboard")

    class GlobalHotKeys:
        instance = None
        press: ClassVar[list] = []

        def __init__(self, hotkeys):
            self.hotkeys = hotkeys
            self.stopped = False
            GlobalHotKeys.instance = self

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def join(self):
            for hotkey in GlobalHotKeys.press:
                self.hotkeys[hotkey]()
            raise KeyboardInterrupt

        def stop(self):
            self.stopped = True

    keyboard.GlobalHotKeys = GlobalHotKeys
    pynput = types.ModuleType("pynput")
    pynput.keyboard = keyboard
    monkeypatch.setitem(sys.modules, "pynput", pynput)
    monkeypatch.setitem(sys.modules, "pynput.keyboard", keyboard)
    return GlobalHotKeys


def test_run_registers_hotkeys_and_stops_on_ctrl_c(fake_pynput, capsys):
    core.PyElant(notifications=False).run()
    listener = fake_pynput.instance
    assert set(listener.hotkeys) == {core.CLIPBOARD_HOTKEY, core.MICROPHONE_HOTKEY}
    assert listener.stopped
    assert "Ctrl+C to quit" in capsys.readouterr().out


def test_clipboard_hotkey_translates_clipboard(fake_pynput, fakes):
    fakes["value"] = "Bonjour"
    fake_pynput.press = [core.CLIPBOARD_HOTKEY]
    pyelant = core.PyElant("fr", "en", notifications=False)
    pyelant.run()
    wait_for_job(pyelant)
    assert fakes["value"] == "[en] Bonjour"


def test_microphone_hotkey_translates_speech(fake_pynput, fake_speech, fakes):
    fake_pynput.press = [core.MICROPHONE_HOTKEY]
    pyelant = core.PyElant(notifications=False)
    pyelant.run()
    wait_for_job(pyelant)
    assert fakes["value"] == "[ja] Hello"


def test_hotkey_ignored_while_translation_in_progress():
    pyelant = core.PyElant(verbose=True)
    ran = []
    pyelant._busy.acquire()
    pyelant._start_job(lambda: ran.append(True))
    assert ran == []


def test_job_failure_is_reported_and_listener_survives(capsys):
    pyelant = core.PyElant()

    def failing_job():
        raise RuntimeError("boom")

    pyelant._start_job(failing_job)
    wait_for_job(pyelant)
    assert "boom" in capsys.readouterr().err


# Notifications ------------------------------------------------------------------------

@pytest.fixture
def fake_notifier(monkeypatch):
    module = types.ModuleType("desktop_notifier")

    class DesktopNotifierSync:
        created = 0
        sent: ClassVar[list] = []

        def __init__(self, app_name):
            DesktopNotifierSync.created += 1
            self.app_name = app_name

        def send(self, title, message):
            DesktopNotifierSync.sent.append((self.app_name, title, message))

    module.DesktopNotifierSync = DesktopNotifierSync
    monkeypatch.setitem(sys.modules, "desktop_notifier", module)
    return DesktopNotifierSync


def test_notification_shows_translation(fake_notifier):
    pyelant = core.PyElant()
    pyelant.translate_to_clipboard("Hi")
    pyelant.translate_to_clipboard("Bye")
    assert fake_notifier.created == 1  # the notifier is created once and reused
    assert fake_notifier.sent == [
        ("pyelant", "Hi", "[ja] Hi was copied to the clipboard"),
        ("pyelant", "Bye", "[ja] Bye was copied to the clipboard"),
    ]


def test_notifications_can_be_disabled(fake_notifier):
    core.PyElant(notifications=False).translate_to_clipboard("Hi")
    assert fake_notifier.created == 0


def test_verbose_logging(capsys):
    core.PyElant(verbose=True, notifications=False).translate_to_clipboard("Hi")
    assert capsys.readouterr().out == "Input: Hi\nOutput: [ja] Hi\n"
    core.PyElant(verbose=False, notifications=False).translate_to_clipboard("Hi")
    assert capsys.readouterr().out == ""
