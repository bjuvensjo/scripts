#!/usr/bin/env python3

from bb_get_branches import get_branches
from bb_utils import get_clone_url, get_project_and_repo


def has_branch(repo_specs, branch):
    for spec, response in get_branches(repo_specs, branch):
        yield spec, branch in [value['displayId'] for value in response['values']]


def main(branch, dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, has in has_branch(specs, branch):
        print('{}/{}, {}: {}'.format(spec[0], spec[1], branch, has))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Check repository branches in Bitbucket')
    parser.add_argument('branch', help='The branch to check')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.branch, args.dirs, args.repos)
