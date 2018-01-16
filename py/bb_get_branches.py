#!/usr/bin/env python3

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo, branch):
    return '/rest/api/1.0/projects/{}/repos/{}/branches?filterText={}'.format(project, repo, branch)


def get_branches(repo_specs, branch=''):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1], branch)
        yield spec, call(uri)


def main(branch='', dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in get_branches(specs, branch):
        print('{}/{}: {}'.format(spec[0], spec[1], [value['displayId'] for value in response['values']]))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get repository branches from Bitbucket')
    parser.add_argument('-b', '--branch',
                        help='Branch filter',
                        default='')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.branch, args.dirs, args.repos)
