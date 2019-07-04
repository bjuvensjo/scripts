#!/usr/bin/env python3
from os import walk
from pprint import pprint
from re import fullmatch


def is_excluded(file, excluded):
    return any([fullmatch(ex, file) for ex in excluded])


def is_included(file, included):
    return any([fullmatch(ex, file) for ex in included])


def get_files(root_dir, excluded=(), included=('*',)):
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


def count_all(dirs=('.',), excluded=(), included=('*',)):
    total_files = 0
    total_lines = 0
    total_words = 0
    total_letters = 0

    for d in dirs:
        for root, file in get_files(d, excluded, included):
            # print(join(root, file))
            total_files += 1
            line_count, word_count, letter_count = count(root, file)
            total_lines += line_count
            total_words += word_count
            total_letters += letter_count

    # return total_files, total_lines, total_words, total_letters
    return {'files': total_files, 'lines': total_lines, 'words': total_words, 'letters': total_letters}


# code_dirs = ['/Users/magnus/git-es']
# code_dirs = ['/Users/magnus/slask/crap/DefaultCollection/CSL']
code_dirs = ['/Users/magnus/slask/CSL/ms.common.signing']
# code_dirs = ['/Users/magnus/slask/wiremock/git/wiremock']
code_dirs = ['/Users/magnus/slask/rsimulator/rsimulator-camel-direct',
             '/Users/magnus/slask/rsimulator/rsimulator-core',
             '/Users/magnus/slask/rsimulator/rsimulator-cxf-rt-transport']
# code_dirs = ['/Users/magnus/git/rsimulator-kotlin/rsimulator-core']
code_dirs = ['/Users/magnus/git-csl/continuous.deployment',
             '/Users/magnus/git-csl/cd.tfs.scripts/src/nexus',
             '/Users/magnus/git-csl/cd.jenkins.job',
             '/Users/magnus/git-csl/cd.jenkins.lib',
             '/Users/magnus/git-csl/cd.jenkins.sync']

result = count_all(
    code_dirs,
    # excluded=('.*Test\..*', '.*IT\..*', 'test.*'),
    included=('.*\.groovy', '.*\.java', '.*\.kt', '.*\.py', 'Jenkinsfile'))
pprint(result)
