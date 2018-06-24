#!/usr/bin/env python3
from multiprocessing.dummy import Pool

from itertools import product

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def set_repo_default_branch(spec, branch):
    request_data = '{{"id":"refs/heads/{}"}}'.format(branch)
    return spec, call('/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(spec[0], spec[1]),
                      request_data,
                      'PUT')


def set_default_branch(repo_specs, branch, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(set_repo_default_branch, product(repo_specs, [branch]))


def main(branch, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in set_default_branch(specs, branch):
        print('{}/{}: {}'.format(spec[0], spec[1], response))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Set default branches for repositories in Bitbucket')
    parser.add_argument('branch', help='The branch to set')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')

    args = parser.parse_args()

    main(args.branch, args.dirs, args.repos, args.projects)
