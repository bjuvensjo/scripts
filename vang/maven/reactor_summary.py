#!/usr/bin/env python3
import argparse
import re
from glob import glob
from itertools import chain

from os.path import realpath
from sys import argv


def get_reactor_summary(mvn_log):
    """ Returns reactor summary. """
    start = False
    lines = []
    single_project_result = 'FAILURE'
    single_project = ''

    for line in mvn_log:
        # Multi module project build
        if re.match(r'.*Reactor Summary.*', line):
            start = True
        if start:
            lines.append(line.strip())
        if start and re.match(r'^.INFO. -.*', line):
            break

        # Single project build
        if re.match(r'.*Building.*', line) and not single_project:
            single_project = line.strip().replace(' Building', '')
        if single_project and re.match(r'.*BUILD SUCCESS.*', line):
            single_project_result = 'SUCCESS'
            break

    if lines:
        return lines[2:-1]

    return [f'{single_project} {single_project_result}']


def get_project(line):
    """ Returns project of reactor line. """
    start = re.search(r' ', line).end()
    end = re.search(r' ', line[start:]).start() + start
    return line[start:end]


def get_successes(reactor_summary):
    """ Returns success projects """
    return [get_project(l) for l in reactor_summary if re.search('SUCCESS', l)]


def get_failures(reactor_summary):
    """ Returns failure projects """
    return [
        get_project(l) for l in reactor_summary if not re.search('SUCCESS', l)
    ]


def read_lines(log_file):  # pragma: no cover
    with open(log_file, 'rt', encoding='utf-8') as f:
        return f.readlines()


def get_summary(mvn_log_files, do_print=False):
    summaries = tuple(
        chain.from_iterable([
            get_reactor_summary(read_lines(log_file))
            for log_file in mvn_log_files
        ]))
    result = get_successes(summaries), get_failures(summaries)
    if do_print:
        print_summary(*result)
    return result


def print_summary(successes, failures):
    length = 80
    lines = []

    def banner(text='', fill=' '):
        s = ' ' + text + ' ' if text else text
        l = int(length / 2 + len(s) / 2)
        return s.rjust(l, fill).ljust(length, fill)

    def artifact(the_id, success, fill='.'):
        outcome = 'SUCCESS' if success else 'FAILURE'
        return the_id + outcome.rjust(length - len(the_id), fill)

    for a_text in ('', 'Summary', ''):
        lines.append(banner(a_text, '*'))
    for an_id in sorted(successes):
        lines.append(artifact(an_id, True))
    for an_id in sorted(failures):
        lines.append(artifact(an_id, False))
    for a_text in ('', ):
        lines.append(banner(a_text, '*'))

    print('\n'.join(lines))


def main(roots, log_file_name):
    successes, failures = get_summary([
        realpath(p) for root in roots
        for p in glob(f'{root}/**/{log_file_name}', recursive=True)
    ])
    print_summary(successes, failures)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Prints reactor summary of Maven build log files')
    parser.add_argument(
        '-d',
        '--roots',
        help='Root directories in which to find Maven log files',
        nargs='*',
        default=['.'])
    parser.add_argument(
        '-l',
        '--log_file_name',
        help='Name of Maven build log file(s)',
        default='mvn.log')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
