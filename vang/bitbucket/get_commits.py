#!/usr/bin/env python3
import argparse
import sys
from itertools import chain

from vang.bitbucket.api import get_all
from vang.bitbucket.utils import get_repo_specs
from vang.core.core import pmap_unordered


# This is not used in this script but still a useful function :)
def get_branch_commits(repo_specs_and_branches, take=sys.maxsize, max_processes=10, filter_function=None):
    def inner(rsb):
        spec = rsb[0]
        branches = rsb[1]
        result = {}
        for b in branches:
            commits = get_all(f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/commits',
                              {'until': b},
                              take)
            result[b] = filter_function(commits) if filter_function else commits

        return result

    return pmap_unordered(
        lambda r: {r[0]: inner(r)},
        repo_specs_and_branches,
        processes=max_processes)


def get_commits(repo_specs, branches=tuple(['']), take=sys.maxsize, max_processes=10):
    return pmap_unordered(
        lambda s: list([s, chain([(b, get_all(f'/rest/api/1.0/projects/{s[0]}/repos/{s[1]}/commits',
                                              {'until': b},
                                              take))
                                  for b in branches])]),
        repo_specs,
        processes=max_processes)


def main(take, branches, sha=False, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, commits in get_commits(specs, branches, take=take):
        if sha:
            for b, cs in commits:
                for c in cs:
                    # print(b, c['id'])
                    print(c['id'])
        else:
            print(f'{spec[0]}/{spec[1]}: {list(commits)}')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get repository commits from Bitbucket')
    parser.add_argument('-b', '--branches', nargs='*', help='Branches filter', default=('',))
    parser.add_argument('--take', '-t', type=int,
                        help='The number of commit from and including HEAD. -1 for all commits',
                        default=sys.maxsize)
    parser.add_argument(
        '-s', '--sha', help='Print only sha', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        '--dirs',
        nargs='*',
        default=['.'],
        help='Git directories to extract commit information from')
    group.add_argument(
        '-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument(
        '-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(sys.argv[1:]).__dict__)
