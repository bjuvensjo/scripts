#!/usr/bin/env python3

import argparse
from sys import argv

from vang.tfs.api import call


def get_repos(organisation, project, names=False, repo_specs=False, urls=False):
    repos = call(f'/{organisation}/{project}/_apis/git/repositories?api-version=3.2')['value']
    if names:
        return [repo['name'] for repo in repos]
    if repo_specs:
        return [f'{organisation}/{project}/{repo["name"]}' for repo in repos]
    if urls:
        return [repo['remoteUrl'] for repo in repos]
    return repos


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get TFS repos')
    parser.add_argument('organisation', help='The TFS organisation')
    parser.add_argument('project', help='The TFS project')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-n', '--names', action='store_true', help='Get only repo names')
    parser.add_argument(
        '-r',
        '--repo_specs',
        help='Print only organisation/project/name',
        action='store_true')
    group.add_argument('-u', '--urls', action='store_true', help='Get only repo urls')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])

    for repo in get_repos(args.organisation, args.project, args.names, args.repo_specs, args.urls):
        print(repo)
