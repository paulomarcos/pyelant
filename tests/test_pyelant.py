import pytest

from pyelant import __main__ as cli
from pyelant import pyelant as core

from .conftest import FakeTranslator


@pytest.mark.parametrize("given, expected", [
    ("ja", "ja"), ("JA", "ja"), ("Japanese", "ja"), ("zh-cn", "zh-cn"), (" fr ", "fr"),
])
def test_normalize_language(given, expected):
    assert core.normalize_language(given) == expected


def test_normalize_language_auto():
    assert core.normalize_language("auto", allow_auto=True) == "auto"
    with pytest.raises(ValueError):
        core.normalize_language("auto")


@pytest.mark.parametrize("bad", ["jp", "kr", "klingon"])
def test_normalize_language_rejects_unknown(bad):
    with pytest.raises(ValueError):
        core.normalize_language(bad)


def test_translate_to_clipboard(fakes):
    pyelant = core.PyElant("en", "ja", notifications=False)
    assert pyelant.translate_to_clipboard("Hello") == "[ja] Hello"
    assert fakes["value"] == "[ja] Hello"
    assert FakeTranslator.calls == [("Hello", "en", "ja")]


def test_translate_clipboard(fakes):
    fakes["value"] = "Bonjour"
    core.PyElant("fr", "en", notifications=False).translate_clipboard()
    assert fakes["value"] == "[en] Bonjour"


def test_translate_clipboard_ignores_empty_clipboard(fakes):
    fakes["value"] = "   "
    core.PyElant(notifications=False).translate_clipboard()
    assert FakeTranslator.calls == []


def test_notification_failure_does_not_break_translation(monkeypatch, fakes):
    pyelant = core.PyElant()

    class BrokenNotifier:
        def send(self, **kwargs):
            raise RuntimeError("no notification server")

    pyelant._notifier = BrokenNotifier()
    assert pyelant.translate_to_clipboard("Hi") == "[ja] Hi"


def test_background_job_errors_are_reported_and_release_lock(capsys):
    pyelant = core.PyElant()

    def failing_job():
        raise RuntimeError("boom")

    pyelant._busy.acquire()
    pyelant._run_job(failing_job)
    assert "boom" in capsys.readouterr().err
    assert pyelant._busy.acquire(blocking=False)


def test_cli_text(capsys, fakes):
    assert cli.main(["-i", "english", "-o", "it", "-t", "Hello", "-dn"]) == 0
    assert capsys.readouterr().out.strip() == "[it] Hello"
    assert fakes["value"] == "[it] Hello"


def test_cli_defaults():
    args = cli.parse_args([])
    assert (args.input_language, args.output_language) == ("en", "ja")


def test_cli_rejects_unknown_language(capsys):
    with pytest.raises(SystemExit):
        cli.parse_args(["-o", "jp"])
    assert "unsupported language" in capsys.readouterr().err


def test_cli_reports_translation_errors(monkeypatch, capsys):
    def fail(self, text):
        raise ConnectionError("offline")

    monkeypatch.setattr(core.PyElant, "translate", fail)
    assert cli.main(["-t", "Hello", "-dn"]) == 1
    assert "offline" in capsys.readouterr().err
