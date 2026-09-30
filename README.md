# PyElant

**Py**thon **E**asy **La**nguage **T**ranslator

[![PyPI](https://img.shields.io/pypi/v/pyelant)](https://pypi.org/project/pyelant/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyelant)](https://pypi.org/project/pyelant/)
[![CI](https://github.com/paulomarcos/pyelant/actions/workflows/ci.yml/badge.svg)](https://github.com/paulomarcos/pyelant/actions/workflows/ci.yml)

PyElant is a small command line tool that translates text with Google Translate and puts the
result on your clipboard.
It can take input from the command line, from the clipboard or from your microphone.

Leave it running in the background and use a hotkey to translate whatever you just copied, or what you
just said. Then paste the translation into your editor, browser or chat without switching windows.

## Installation

PyElant requires Python 3.10 or newer.

```sh
pip install pyelant
```

To also use microphone input, install the `mic` extra:

```sh
pip install "pyelant[mic]"
```

[pipx](https://pipx.pypa.io/) or [uv](https://docs.astral.sh/uv/) also work well for command line
tools like this one: `pipx install pyelant` or `uv tool install pyelant`.

### System requirements

- **Linux**: clipboard access needs `xclip` or `xsel` (X11) or `wl-clipboard` (Wayland). Global
  hotkeys only work under X11 (including XWayland apps), not native Wayland apps. Microphone
  input needs the PortAudio headers if no PyAudio wheel exists for your platform:

  ```sh
  sudo apt install xclip              # clipboard
  sudo apt install portaudio19-dev    # only for microphone input
  ```

- **macOS**: to use the hotkeys, give your terminal app permission under *System Settings →
  Privacy & Security → Accessibility* (and *Input Monitoring*). Microphone input also needs
  microphone permission. Desktop notifications may not appear when PyElant runs from a plain
  terminal. Translations still work as normal.

- **Windows**: no extra setup needed.

## Usage

There are three ways to use PyElant:

1. **Command line**: translate a piece of text right away.
2. **Clipboard**: press a hotkey to translate what you copied.
3. **Microphone**: press a hotkey and speak.

### Command line

Pass the text with `-t` / `--text`. PyElant prints the translation and copies it to your clipboard:

```sh
pyelant -t "This sentence will be translated to Japanese."
```

### Clipboard

Start PyElant with no text and leave it running in the background:

```sh
pyelant
```

Copy some text, then press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>E</kbd>. The translation replaces the
clipboard contents, ready to paste.

### Microphone

With PyElant running in the background (see above), press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>M</kbd>,
say something and wait. When the translation is done it is copied to your clipboard. This mode
needs the `mic` extra.

Press <kbd>Ctrl</kbd>+<kbd>C</kbd> in the terminal to stop PyElant.

## Choosing languages

By default PyElant translates from English (`en`) to Japanese (`ja`). Use `-i` / `--input_language`
and `-o` / `--output_language` to change this. Languages can be given as a code (`pt`, `ko`,
`zh-cn`) or a name (`portuguese`, `korean`). Use `-i auto` to detect the input language
automatically (for text only, not for microphone input).

```sh
pyelant -i pt -o en    # run in the background, translating Portuguese to English
pyelant -i fr -o ko    # run in the background, translating French to Korean
pyelant -i en -o it -t "This sentence will be translated from English to Italian."
```

Each run uses a single pair of languages. To switch languages, stop PyElant and start it again.

## All options

| Option | Description |
| --- | --- |
| `-i`, `--input_language` | Language to translate from. Default: `en`. |
| `-o`, `--output_language` | Language to translate to. Default: `ja`. |
| `-t`, `--text` | Text to translate. Without it, PyElant runs in the background. |
| `-dn`, `--disable_notification` | Do not show a desktop notification with the translation. |
| `-v`, `--verbose` | Print extra information. |
| `--version` | Show the version and exit. |

`python -m pyelant` works as well as the `pyelant` command.

## How it works

Translations use Google Translate through [googletrans](https://github.com/ssut/py-googletrans), and
speech is recognized with [SpeechRecognition](https://github.com/Uberi/speech_recognition). Both
use free, unofficial Google endpoints, so an internet connection is required and heavy use may be
rate limited.

## Development

```sh
git clone https://github.com/paulomarcos/pyelant
cd pyelant
uv run --all-extras pytest    # run the tests (offline)
uv run pytest -m network      # run the live tests against Google Translate
uv run ruff check             # lint
uv build                      # build the sdist and wheel
```

## License

MIT License. See [LICENSE.txt](LICENSE.txt).
