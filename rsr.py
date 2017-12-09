#!/usr/bin/env python3

from os import remove, rename, replace, walk
from os.path import join, sep
from re import fullmatch, sub
from sys import argv


def _replace_in_file(from_pattern, to_pattern, path):
    content_changed = False
    with open(path, "tr", encoding="UTF-8") as old_file, open(path + '.tmp', "tw", encoding="UTF-8") as new_file:
        for line in old_file:
            new_line = sub(from_pattern, to_pattern, line)
            content_changed = content_changed or new_line != line
            new_file.write(new_line)
    if content_changed:
        replace(path + '.tmp', path)
    else:
        remove(path + '.tmp')


def _replace_file(from_pattern, to_pattern, path, file):
    new_file = sub(from_pattern, to_pattern, file)
    if new_file != file:
        rename(join(path, file),
               join(path, new_file))


def _in(name, regexps):
    return any(fullmatch(name, e) for e in regexps)


def _rsr(root, excludes, from_pattern, to_pattern):
    for dir_path, dir_names, files in walk(root, False):
        if not any(_in(d, excludes) for d in dir_path.split(sep)):
            for file in files:
                if not _in(file, excludes):
                    _replace_in_file(from_pattern, to_pattern, join(dir_path, file))
                    _replace_file(from_pattern, to_pattern, dir_path, file)

            for dir_name in dir_names:
                if not _in(dir_name, excludes):
                    _replace_file(from_pattern, to_pattern, dir_path, dir_name)


def rsr(from_pattern, to_pattern, dirs):
    for dir in dirs:
        _rsr(dir, ['.git', '.gitignore'], from_pattern, to_pattern)


if __name__ == "__main__":
    dirs = ["."]
    branch = None

    if len(argv) < 3:
        print("Must specify from_pattern and to_pattern")
    else:
        if len(argv) > 3:
            dirs = argv[3:]
        rsr(argv[1], argv[2], dirs)
