"""Contract tests against the real third-party libraries.

These don't touch the network. They fail if an upgrade changes an API PyElant relies
on, which the mocked unit tests can't catch.
"""

import inspect
import subprocess
import sys
from importlib.metadata import entry_points, version

import pyelant
from pyelant import pyelant as core

from .conftest import require


def test_googletrans_translator_api():
    from googletrans import Translator

    assert hasattr(Translator, "__aenter__") and hasattr(Translator, "__aexit__")
    assert inspect.iscoroutinefunction(Translator.translate)
    params = inspect.signature(Translator.translate).parameters
    assert {"src", "dest"} <= set(params)


def test_googletrans_language_tables():
    from googletrans import LANGCODES, LANGUAGES

    assert LANGUAGES["ja"] == "japanese"
    assert LANGCODES["japanese"] == "ja"
    for code in LANGUAGES:
        assert core.normalize_language(code) == code


def test_pyperclip_api():
    import pyperclip

    assert callable(pyperclip.copy) and callable(pyperclip.paste)


def test_desktop_notifier_api():
    from desktop_notifier import DesktopNotifierSync

    assert "app_name" in inspect.signature(DesktopNotifierSync).parameters
    assert {"title", "message"} <= set(inspect.signature(DesktopNotifierSync.send).parameters)


def test_speech_recognition_api():
    sr = require("speech_recognition")
    require("pyaudio")

    assert "language" in inspect.signature(sr.Recognizer.recognize_google).parameters
    for name in ("Microphone", "UnknownValueError", "RequestError"):
        assert hasattr(sr, name)


def test_pynput_parses_hotkeys():
    keyboard = require("pynput.keyboard")

    for hotkey in (core.CLIPBOARD_HOTKEY, core.MICROPHONE_HOTKEY):
        assert len(keyboard.HotKey.parse(hotkey)) == 3
    assert inspect.isclass(keyboard.GlobalHotKeys)


def test_package_metadata():
    assert version("pyelant") == pyelant.__version__
    scripts = entry_points(group="console_scripts", name="pyelant")
    assert [script.value for script in scripts] == ["pyelant.__main__:main"]


def test_python_dash_m_runs():
    result = subprocess.run([sys.executable, "-m", "pyelant", "--version"],
                            capture_output=True, text=True, check=True)
    assert result.stdout.strip() == f"pyelant {pyelant.__version__}"
