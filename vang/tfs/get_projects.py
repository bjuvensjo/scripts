#!/usr/bin/env python3

import argparse
from sys import argv

from vang.tfs.api import call


def get_projects(organisation, project_specs=False, names=False):
    projects = call(f'/{organisation}/_apis/projects?api-version=3.2')['value']

    if names:
        return [project['name'] for project in projects]
    if project_specs:
        return [f'{organisation}/{project["name"]}' for project in projects]

    return projects


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get TFS projects')
    parser.add_argument('organisation', help='The TFS organisation')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-n', '--names', action='store_true', help='Get only project names')
    parser.add_argument(
        '-p',
        '--project_specs',
        action='store_true',
        help='Get only organisation/project')

    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])

    for project in get_projects(
            args.organisation,
            args.project_specs,
            args.names,
    ):
        print(project)
