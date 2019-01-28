#!/usr/bin/env python3
from argparse import ArgumentParser
from glob import glob
from os import makedirs
from os.path import exists
from re import match
from sys import argv

from vang.pio.shell import run_command


def is_excluded(py_file):
    return any((match(regexp,
                      py_file.split('/')[-1])
                for regexp in ['__init__.py', '.*slask.*', '.*Slask.*']))


def has_main(py_file):
    main_lines = [
        "if __name__ == '__main__':",
        'if __name__ == "__main__":',
    ]
    with open(py_file, 'rt', encoding='utf-8') as f:
        for line in f:
            # if line and match(r'.*if __name__ == ("|\')__main__("|\'): *',
            #                   line):
            print(line)
            if line.strip() in main_lines:
                return True
    return False


def map_to_link_name(main_file):
    main_file_package, main_file_name = main_file.split('/')[-2:]
    return f'{main_file_package}-{main_file_name[:-3].replace("_", "-")}'


def create_symlinks(source, target):
    if not exists(target):
        makedirs(target)

    for main_file in [
            f for f in glob(f'{source}/**/*.py', recursive=True)
            if has_main(f) and not is_excluded(f)
    ]:
        link_file = f'{target}/{map_to_link_name(main_file)}'
        if exists(link_file):
            print(f'{link_file} already exists')
        else:
            command = f'ln -s {main_file} {link_file}'
            print(command)
            run_command(command)


def parse_args(args):
    parser = ArgumentParser(description='Create symlinks')
    parser.add_argument('source', help='Source root')
    parser.add_argument('target', help='Target')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    create_symlinks(**parse_args(argv[1:]).__dict__)

