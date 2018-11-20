#!/usr/bin/env python3
import argparse
import re
from sys import argv

from vang.bitbucket.get_clone_urls import get_clone_urls
from vang.bitbucket.get_projects import get_projects


def get_clone_urls_grep(patterns, command=False):
    return get_clone_urls([
        p['key'] for p in get_projects()
        if any((re.match(r'{}'.format(pattern), p['key'])
                for pattern in patterns))
    ], command)


def main(patterns, command):
    for clone_dir, project, repo, clone_url in get_clone_urls_grep(
            patterns, command):
        print(clone_url)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get clone urls for project patterns from Bitbucket')
    parser.add_argument('patterns', nargs='+', help='The patterns')
    parser.add_argument(
        '-c', '--command', help='Print as clone commands', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
