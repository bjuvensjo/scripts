#!/usr/bin/env python3
import argparse
from itertools import product
from multiprocessing.dummy import Pool
from sys import argv

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def set_repo_default_branch(spec, branch):
    request_data = {'id': f'refs/heads/{branch}'}
    return spec, call(
        f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/branches/default',
        request_data,
        only_response_code=True,
        method='PUT',
    )


def set_default_branch(repo_specs, branch, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(set_repo_default_branch,
                            product(repo_specs, [branch]))


def main(branch, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in set_default_branch(specs, branch):
        print(f'{spec[0]}/{spec[1]}: {response}')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Set default branches for repositories in Bitbucket')
    parser.add_argument('branch', help='The branch to set')
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
