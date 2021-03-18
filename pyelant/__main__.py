"""
PyElant main module.

 @brief   PyElant
 @author  Paulo Marcos
 @date    2021-03-19
 Copyright (c) 2021 paulomarcosdj  <@> outlook.com
"""

import argparse
from .pyelant import PyElant

def main():
    parser = argparse.ArgumentParser(description='PyElant: insert input and output languages.')
    parser.add_argument('-i', '--input_language', type=str,
                        help='Input language to be translated. Example: "en", "jp", "fr".')
    parser.add_argument('-o', '--output_language', type=str,
                        help='Output language desired. Example: "jp", "fr", "en".')
    parser.add_argument('-t', '--text', type=str,
                        help='Text to be translated. Example "Hello world."')
    parser.add_argument('-dn', '--disable_notification', action="store_true",
                        help='Disable system notification displaying result of the translations.')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Verbose mode')

    args = parser.parse_args()
    PyElant(args.input_language,
            args.output_language,
            args.text,
            args.disable_notification,
            args.verbose)


if __name__ == "__main__":
    main()