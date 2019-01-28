#!/usr/bin/env python3
import argparse
from itertools import product
from multiprocessing.dummy import Pool
from sys import argv

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def fork_repo(spec, fork_project):
    uri = f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}'
    request_data = {'slug': spec[1], 'project': {'key': fork_project}}
    return spec, call(uri, request_data, 'POST')


def fork_repos(repo_specs, fork_project, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(fork_repo, product(repo_specs, [fork_project]))


def main(fork_project, dirs, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in fork_repos(specs, fork_project):
        print(f'{spec[0]}/{spec[1]}: {response}')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Fork Bitbucket repos')
    parser.add_argument('fork_project', help='Fork project')
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
