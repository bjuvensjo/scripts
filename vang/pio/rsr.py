#!/usr/bin/env python3

from os import remove, rename, replace, walk
from os.path import join, sep
from re import fullmatch, sub


def _replace(regexp):
    return lambda s, old, new: sub(old, new, s) if regexp else s.replace(old, new)


def _replace_in_file(old, new, path, repl):
    content_changed = False
    with open(
            path, 'tr', encoding='UTF-8', errors='ignore') as old_file, open(
                path + '.tmp', 'tw', encoding='UTF-8') as new_file:
        for line in old_file:
            new_line = repl(line, old, new)
            content_changed = content_changed or new_line != line
            new_file.write(new_line)
    replace(path + '.tmp', path) if content_changed else remove(path + '.tmp')


def _replace_file(old, new, path, file, repl):
    new_file = repl(file, old, new)
    if new_file != file:
        rename(join(path, file), join(path, new_file))


def _in(name, regexps):
    return any(fullmatch(name, e) for e in regexps)


def _rsr(root, excludes, old, new, repl):
    for dir_path, dir_names, files in walk(root, False):
        if not any(_in(d, excludes) for d in dir_path.split(sep)):
            for file in files:
                if not _in(file, excludes):
                    _replace_in_file(old, new, join(dir_path, file), repl)
                    _replace_file(old, new, dir_path, file, repl)

            for dir_name in dir_names:
                if not _in(dir_name, excludes):
                    _replace_file(old, new, dir_path, dir_name, repl)


def rsr(old, new, dirs, repl):
    for d in dirs:
        _rsr(d, ['.git', '.gitignore', 'target'], old, new, repl)


def main(old, new, dirs, regexp):
    rsr(old, new, dirs, _replace(regexp))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Recursive search and replace of directories, files and file contents')
    parser.add_argument('old', help='Old value')
    parser.add_argument('new', help='New value')
    parser.add_argument('-d', '--dirs', nargs='*', default=['.'])
    parser.add_argument('-r', '--regexp', action='store_true')
    args = parser.parse_args()

    main(args.old, args.new, args.dirs, args.regexp)
