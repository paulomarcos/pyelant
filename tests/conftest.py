import importlib
import os
from types import SimpleNamespace
from typing import ClassVar

import pytest

from pyelant import pyelant as core


class FakeTranslator:
    """Stands in for googletrans.Translator so tests never hit the network."""

    calls: ClassVar[list] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def translate(self, text, src, dest):
        FakeTranslator.calls.append((text, src, dest))
        return SimpleNamespace(text=f"[{dest}] {text}")


@pytest.fixture(autouse=True)
def fakes(request, monkeypatch):
    """Fake the translator and clipboard, except in tests marked `network`."""
    if request.node.get_closest_marker("network"):
        return None
    FakeTranslator.calls = []
    clipboard = {"value": ""}
    monkeypatch.setattr(core, "Translator", FakeTranslator)
    monkeypatch.setattr(core.pyperclip, "copy", lambda text: clipboard.update(value=text))
    monkeypatch.setattr(core.pyperclip, "paste", lambda: clipboard["value"])
    return clipboard


def require(module_name):
    """Import an optional module, skipping the test locally but failing on CI if unusable."""
    try:
        return importlib.import_module(module_name)
    except Exception as error:  # e.g. pynput raises when there is no display
        if os.environ.get("CI"):
            raise
        pytest.skip(f"{module_name} is not usable here: {error}")
