#!/usr/bin/env python3
from multiprocessing.dummy import Pool

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def get_repo_default_branch(spec):
    return spec, call('/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(spec[0], spec[1]))


def get_default_branch(repo_specs, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.map(get_repo_default_branch, repo_specs)


def main(dirs, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in get_default_branch(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], response['displayId']))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get default repository branches from Bitbucket')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.dirs, args.repos, args.projects)
