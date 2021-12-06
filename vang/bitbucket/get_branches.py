#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.api import get_all
from vang.bitbucket.utils import get_repo_specs
from vang.core.core import pmap_unordered


def get_branches(repo_specs, branch='', max_processes=10):
    return pmap_unordered(
        lambda s: (s, get_all(f'/rest/api/1.0/projects/{s[0]}/repos/{s[1]}/branches',
                              {'filterText': branch})),
        repo_specs,
        processes=max_processes)


def main(branch='', name=False, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, branches in get_branches(specs, branch):
        for b in branches:
            if name:
                print(b['displayId'])
            else:
                print(f'{spec[0]}/{spec[1]}: {b["displayId"]}')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get repository branches from Bitbucket')
    parser.add_argument('-b', '--branch', help='Branch filter', default='')
    parser.add_argument(
        '-n', '--name', help='Print only branch name', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        '--dirs',
        nargs='*',
        default=['.'],
        help='Git directories to extract repo information from')
    group.add_argument(
        '-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument(
        '-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
