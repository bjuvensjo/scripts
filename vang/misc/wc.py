#!/usr/bin/env python3
import argparse
from os import walk
from pprint import pprint
from re import fullmatch
from sys import argv


def is_excluded(file, excluded):
    return any([fullmatch(ex, file) for ex in excluded])


def is_included(file, included):
    return any([fullmatch(ex, file) for ex in included])


def get_files(root_dir, excluded=(), included=('.*',)):
    for root, dirs, files in walk(root_dir):
        for f in files:
            if is_included(f, included) and not is_excluded(f, excluded):
                yield root, f


def count_words(line):
    n = 0
    for s in line.split(' '):
        if s.strip():
            n += 1
    return n


def count_letters(line):
    return len(line.strip())


def count(root, file):
    line_count = 0
    word_count = 0
    letter_count = 0
    with open(f'{root}/{file}', 'rt', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                line_count += 1
                word_count += count_words(line)
                letter_count += count_letters(line)
    return line_count, word_count, letter_count


def count_all(dirs=('.',), excluded=(), included=('.*',)):
    total_files = 0
    total_lines = 0
    total_words = 0
    total_letters = 0

    for d in dirs:
        for root, file in get_files(d, excluded, included):
            total_files += 1
            line_count, word_count, letter_count = count(root, file)
            total_lines += line_count
            total_words += word_count
            total_letters += letter_count

    return {'files': total_files, 'lines': total_lines, 'words': total_words, 'letters': total_letters}


def parse_args(args):
    parser = argparse.ArgumentParser(description='Count files, lines, words and letters.')
    parser.add_argument('-d', '--dirs', nargs='*', default=['.'], help='Directories to count in')
    parser.add_argument('-e', '--excluded', nargs='*', default=[],
                        help='File name exclusion patterns, e.g .*Test\\..* .*IT\\..*')
    parser.add_argument('-i', '--included', nargs='*', default=['.*'],
                        help='File name inclusion patterns, e.g .*\\.groovy .*\\.java .*\\.py')
    return parser.parse_args(args)


def main(dirs=('.',), excluded=(), included=('.*',)):
    result = count_all(dirs, excluded=excluded, included=included)
    pprint(result)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)

# code_dirs = ['/Users/magnus/git/rsimulator/rsimulator-camel-direct',
#              '/Users/magnus/git/rsimulator/rsimulator-core',
#              '/Users/magnus/git/rsimulator/rsimulator-cxf-rt-transport']
# code_dirs = ['/Users/magnus/git/rsimulator']
#
# result = count_all(
#     code_dirs,
#     # excluded=('.*Test\..*', '.*IT\..*', 'test.*'),
#     included=('.*\.groovy', '.*\.java', '.*\.kt', '.*\.py', 'Jenkinsfile'))
# pprint(result)
