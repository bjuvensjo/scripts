#!/usr/bin/env python3

import argparse
from sys import argv

from vang.tfs.api import call
from vang.tfs.get_projects import get_projects


def get_repos(organisations=None,
              projects=None,
              names=False,
              repo_specs=False,
              urls=False):
    if organisations:
        projects = get_projects(organisations, project_specs=True)
    if not projects:
        return []
    repos = [(project, repo) for project in projects for repo in call(
        f'/{project}/_apis/git/repositories?api-version=3.2')['value']]
    if names:
        return [repo[1]['name'] for repo in repos]
    if repo_specs:
        return [f'{repo[0]}/{repo[1]["name"]}' for repo in repos]
    if urls:
        return [repo[1]['remoteUrl'] for repo in repos]
    return repos


def main(organisations, projects, names, repo_specs, urls):
    for repo in get_repos(organisations, projects, names, repo_specs, urls):
        print(repo)


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

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        '-n', '--names', action='store_true', help='Get only repo names')
    optional_group.add_argument(
        '-r',
        '--repo_specs',
        help='Print only organisation/project/name',
        action='store_true')
    optional_group.add_argument(
        '-u', '--urls', action='store_true', help='Get only repo urls')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
