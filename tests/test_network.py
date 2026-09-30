"""Live tests against Google Translate. Run with: pytest -m network"""

import pytest

from pyelant import pyelant as core

pytestmark = pytest.mark.network


def test_live_translation():
    translation = core.PyElant("en", "ja").translate("Good morning")
    assert translation
    assert translation != "Good morning"


def test_live_translation_auto_detect():
    translation = core.PyElant("auto", "en").translate("Bonjour tout le monde")
    assert "everyone" in translation.lower()
