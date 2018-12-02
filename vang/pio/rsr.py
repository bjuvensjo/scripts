#!/usr/bin/env python3
import argparse
from os import remove, rename, replace, walk
from os.path import join, sep
from re import fullmatch, sub
from sys import argv


def get_replace_function(regexp=False):
    return lambda s, old, new: sub(old, new, s) if regexp else s.replace(old,
                                                                         new)


def _replace_in_file(old, new, path, replace_function):
    content_changed = False
    with open(
            path,
            'tr',
            encoding='UTF-8',
            errors='ignore',
    ) as old_file, open(
        path + '.tmp',
        'tw',
        encoding='UTF-8',
    ) as new_file:
        for line in old_file:
            new_line = replace_function(line, old, new)
            content_changed = content_changed or new_line != line
            new_file.write(new_line)
    replace(path + '.tmp', path) if content_changed else remove(path + '.tmp')


def _replace_file(old, new, path, file, replace_function):
    new_file = replace_function(file, old, new)
    if new_file != file:
        rename(join(path, file), join(path, new_file))


def _in(name, regexps):
    return any(fullmatch(name, e) for e in regexps)


def _rsr(root, excludes, old, new, replace_function):
    for dir_path, dir_names, files in walk(root, False):
        if not any(_in(d, excludes) for d in dir_path.split(sep)):
            for file in files:
                if not _in(file, excludes):
                    _replace_in_file(old, new, join(dir_path, file),
                                     replace_function)
                    _replace_file(old, new, dir_path, file, replace_function)

            for dir_name in dir_names:
                if not _in(dir_name, excludes):
                    _replace_file(old, new, dir_path, dir_name,
                                  replace_function)


def rsr(old, new, dirs, replace_function):
    for d in dirs:
        _rsr(d, ['.git', '.gitignore', 'target'], old, new, replace_function)


def main(old, new, dirs, regexp):
    rsr(old, new, dirs, get_replace_function(regexp))


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Recursive search and replace of '
                    'directories, files and file contents')
    parser.add_argument('old', help='Old value')
    parser.add_argument('new', help='New value')
    parser.add_argument('-d', '--dirs', nargs='*', default=['.'])
    parser.add_argument('-r', '--regexp', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
