#!/usr/bin/env python3
from multiprocessing.dummy import Pool

from itertools import chain

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def get_repo_default_branch(spec):
    return spec, call('/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(spec[0], spec[1]))


def get_default_branch(repo_specs, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return chain(pool.map(get_repo_default_branch, repo_specs))


def main(dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in get_default_branch(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], response['displayId']))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get repository branches from Bitbucket')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.dirs, args.repos)
