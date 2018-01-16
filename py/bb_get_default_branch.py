#!/usr/bin/env python3

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(project, repo)


def get_default_branch(repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        yield spec, call(uri)


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
