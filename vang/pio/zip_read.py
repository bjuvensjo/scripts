#!/usr/bin/env python3

from argparse import ArgumentParser
from re import fullmatch
from sys import argv
from zipfile import ZipFile


def is_included(patterns, name):
    return any([fullmatch(r'{}'.format(p), name) for p in patterns])


def zip_read(zip_file, patterns, encoding='utf-8'):  # pragma: no cover
    with ZipFile(zip_file, 'r') as z:
        return [(name, z.read(name).decode(encoding)) for name in z.namelist()
                if is_included(patterns, name)]


def main(zip_file, patterns, only_content=False, encoding='utf-8'):
    for file_name, content in zip_read(zip_file, patterns, encoding):
        print('#' * 80)
        if not only_content:
            print('#' * 5, file_name, '#' * 5)
        print(content)


def parse_args(args):
    parser = ArgumentParser(
        description='Read content from files in zip (jar etc)')
    parser.add_argument(
        'zip_file',
        help='The zip file',
    )
    parser.add_argument(
        '-p',
        '--patterns',
        nargs='+',
        default=['.*'],
        help='File name patterns',
    )
    parser.add_argument(
        '-o',
        '--only_content',
        action='store_true',
        help='Print only content',
    )
    parser.add_argument(
        '-e',
        '--encoding',
        default='utf-8',
        help='File encoding',
    )

    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
