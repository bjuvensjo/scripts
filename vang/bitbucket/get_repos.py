#!/usr/bin/env python3
import argparse
import itertools
from sys import argv

from vang.bitbucket.api import get_all
from vang.core.core import pmap_unordered


def get_repos(project, only_name=False, only_spec=False):
    for value in get_all(f'/rest/api/1.0/projects/{project}/repos'):
        if only_name:
            yield value['slug']
        elif only_spec:
            yield value['project']['key'], value['slug']
        else:
            yield value


def get_all_repos(projects, max_processes=10, only_name=False, only_spec=False):
    return itertools.chain.from_iterable(
        pmap_unordered(
            lambda p: get_repos(p, only_name, only_spec),
            projects,
            processes=max_processes))


def main(projects, name, repo_specs):
    for repo in get_all_repos(projects, only_name=name, only_spec=repo_specs):
        if repo_specs:
            print(f'{repo[0]}/{repo[1]}')
        else:
            print(repo)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get repos from Bitbucket')
    parser.add_argument('projects', nargs='+', help='Project keys')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-n', '--name', help='Print only repo name', action='store_true')
    group.add_argument(
        '-r',
        '--repo_specs',
        help='Print only project_key/name',
        action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
