"""Command line interface for PyElant."""

import argparse
import sys

from . import __version__
from .pyelant import PyElant, normalize_language


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="pyelant",
        description="Translate text from the command line, clipboard or microphone "
                    "and place the result on the clipboard.")
    parser.add_argument('-i', '--input_language', default="en",
                        help='Language to translate from, as a code or name. '
                             'Example: "en", "ja", "french". Default: "en".')
    parser.add_argument('-o', '--output_language', default="ja",
                        help='Language to translate to, as a code or name. '
                             'Example: "ja", "fr", "english". Default: "ja".')
    parser.add_argument('-t', '--text',
                        help='Text to translate. Without it, PyElant runs in the '
                             'background and waits for hotkeys.')
    parser.add_argument('-dn', '--disable_notification', action="store_true",
                        help='Disable the desktop notification showing the translation.')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Verbose mode.')
    parser.add_argument('--version', action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)
    try:
        args.input_language = normalize_language(args.input_language, allow_auto=True)
        args.output_language = normalize_language(args.output_language)
    except ValueError as error:
        parser.error(str(error))
    return args


def main(argv=None):
    args = parse_args(argv)
    pyelant = PyElant(args.input_language,
                      args.output_language,
                      notifications=not args.disable_notification,
                      verbose=args.verbose)

    if args.text is None:
        pyelant.run()
        return 0

    try:
        print(pyelant.translate_to_clipboard(args.text))
    except Exception as error:  # noqa: BLE001
        print(f"pyelant: translation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
