#!/usr/bin/env python3

import argparse
from sys import argv

from vang.tfs.api import call
from vang.tfs.get_repos import get_repos


def get_repo_branches(organisation, project, repository, ref_filter='refs/heads'):
    f = f'/{ref_filter}' if ref_filter else ''
    uri = f'/{organisation}/{project}/_apis/git/repositories/{repository}{f}?api-version=3.2'
    return call(uri)['value']


def get_branches(organisations=None,
                 projects=None,
                 repos=None,
                 names=False):
    if organisations:
        repos = get_repos(organisations=organisations, repo_specs=True)
    if projects:
        repos = get_repos(projects=projects, repo_specs=True)

    branch_specs = [(repo, get_repo_branches(*repo.split('/'))) for repo in repos]
    if names:
        return [(repo, [branch['name'] for branch in branches]) for repo, branches in branch_specs]
    return branch_specs


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get TFS repos')
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument(
        '-o',
        '--organisations',
        nargs='+',
        help='TFS organisations, e.g organisation')
    required_group.add_argument(
        '-p',
        '--projects',
        nargs='+',
        help='TFS projects, e.g organisation/project')
    required_group.add_argument(
        '-r',
        '--repos',
        nargs='+',
        help='TFS repos, e.g organisation/project/repo')

    parser.add_argument(
        '-n', '--names', action='store_true', help='Get only repo names')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])

    for repo, branches in get_branches(args.organisations, args.projects, args.repos, args.names):
        for branch in branches:
            print(f'{repo}: {branch.split("/")[-1] if args.names else branch}')

