# Changelog

## 0.2.0

PyElant works again on current Python versions (3.10 to 3.14).

### Added
- `pyelant` command. `python -m pyelant` still works.
- `--version` option.
- Languages can be given by name (`-o korean`), and `-i auto` detects the input language.
- `-t` prints the translation as well as copying it.
- Desktop notifications on macOS and Windows, not only Linux.

### Changed
- Microphone support is an optional extra: `pip install "pyelant[mic]"`.
- Stop PyElant with Ctrl+C in the terminal. Pressing Esc no longer quits it.
- Unknown language codes are rejected with a clear error.
- Requires Python 3.10 or newer.

### Fixed
- `pyelant -t "..."` crashed instead of translating.
- Installation failed on Python 3.12 and newer.
- Listening to the microphone froze the hotkeys, and one failed translation stopped the program.

## 0.1

First release.
