#!/usr/bin/env python3
from argparse import ArgumentParser
from difflib import ndiff
from sys import argv
from zipfile import ZipFile, ZIP_DEFLATED


def diff(name, content, updated_content):
    diffs = list(ndiff(content.splitlines(1), updated_content.splitlines(1)))
    if diffs:
        print(f"{name}\n{''.join(diffs)}")


def replace(content, replacements):
    updated_content = content
    for old, new in replacements.items():
        updated_content = updated_content.replace(old, new)
    return updated_content


def zip_read(zip_file, encoding='utf-8'):
    with ZipFile(zip_file, 'r') as z:
        for name in z.namelist():
            yield (name, z.read(name).decode(encoding))


def update_zip(original_zip, updated_zip, replacements, encoding='utf-8', verbose=False):
    with ZipFile(updated_zip, 'w', compression=ZIP_DEFLATED) as z:
        for name, content in zip_read(original_zip, encoding=encoding):
            updated_content = replace(content, replacements)
            if verbose:
                diff(name, content, updated_content)
            z.writestr(name, updated_content)


def main(original_zip, updated_zip, replacements, encoding='utf-8', verbose=False):
    # make a dict of replacements list
    d = dict(zip(replacements[::2], replacements[1::2]))
    update_zip(original_zip, updated_zip, d, encoding, verbose)


def parse_args(args):
    parser = ArgumentParser(description='Replace in zip (e.g. zip, jar or war')
    parser.add_argument('original_zip', help='original zip path')
    parser.add_argument('updated_zip', help='updated zip path')
    parser.add_argument(
        'replacements',
        nargs='+',
        help='A list of replacements to be done in the zip. Index 0 will be replaced with index 1 and so on.'
    )
    parser.add_argument(
        '-e',
        '--encoding',
        default='utf-8',
        help='TFS projects, e.g organisation/project')
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Verbose output')

    return parser.parse_args(args)


if __name__ == '__main__':
    """
    Example:
    ./replace_in_zip.py original.zip updated.zip old1 new1 old2 new2 oldN newN
    """
    main(**parse_args(argv[1:]).__dict__)
