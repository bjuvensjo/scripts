#!/usr/bin/env python3
import argparse
from os import walk, rename, makedirs, listdir, rmdir
from os.path import join, sep
from sys import argv
from typing import Iterable, Callable

from vang.pio.rsr import _replace_in_file, _in


def file_content_replace_function(line: str, old: str, new: str) -> str:
    line = line.replace(old, new)
    line = line.replace(old.replace('.', sep), new.replace('.', sep))

    # line = line.replace(f'<groupId>{old}</groupId>', f'<groupId>{new}</groupId>')
    # line = line.replace(f'"{old}', f'"{new}')
    # line = line.replace('{' + old, '{' + new)
    # line = line.replace('<' + old, '<' + new)
    # line = line.replace('=' + old, '=' + new)
    # line = line.replace("='" + old, "='" + new)
    # line = line.replace(old.replace('.', sep), new.replace('.', sep))
    # line = sub(f'^package +{old}', f'package {new}', line)
    # line = sub(f'^import +{old}', f'import {new}', line)
    # line = sub(f'^import +static +{old}', f'import static {new}', line)
    return line


def file_path_replace_function(file: str, old: str, new: str) -> str:
    return file.replace(old.replace('.', sep), new.replace('.', sep))


def _replace_file(old: str, new: str, path: str, file: str, replace_function: Callable[[str, str, str], str]) -> None:
    new_path = replace_function(path, old, new)
    if new_path != path:
        makedirs(new_path, exist_ok=True)
        rename(join(path, file), join(new_path, file))


def _regroup(root: str, excludes: Iterable[str], old: str, new: str) -> None:
    for dir_path, dir_names, files in walk(root, False):
        if not any(_in(d, excludes) for d in dir_path.split(sep)):
            for file in files:
                if not _in(file, excludes):
                    _replace_in_file(old, new, join(dir_path, file), file_content_replace_function)
                    _replace_file(old, new, dir_path, file, file_path_replace_function)

            for dir_name in dir_names:
                if not listdir(join(dir_path, dir_name)):
                    rmdir(join(dir_path, dir_name))


def regroup(old: str, new: str, dirs: Iterable[str]) -> None:
    for d in dirs:
        _regroup(d, ['.git', '.gitignore', 'target'], old, new)


def main(old: str, new: str, dirs: Iterable[str]) -> None:
    regroup(old, new, dirs)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Change group for maven module, including package, all its imports and path references')
    parser.add_argument('old', help='old group')
    parser.add_argument('new', help='new group')
    parser.add_argument('-d', '--dirs', nargs='*', default=['.'])
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
