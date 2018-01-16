#!/usr/bin/env python3

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(project, repo)


def set_default_branch(repo_specs, branch):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = '{{"id":"refs/heads/{}"}}'.format(branch)
        yield spec, call(uri, request_data, 'PUT')


def main(branch, dirs, repos):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in set_default_branch(specs, branch):
        print('{}/{}: {}'.format(spec[0], spec[1], response))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Set default branch for repositories in Bitbucket')
    parser.add_argument('branch', help='The branch to set')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.branch, args.dirs, args.repos)
