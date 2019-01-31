#!/usr/bin/env python3

import argparse
from fnmatch import fnmatch
from sys import argv

from vang.tfs.api import call
from vang.tfs.get_projects import get_projects


def list_release_definitions(organisations=None,
                             projects=None,
                             filter_name=None):
    if organisations:
        projects = get_projects(organisations, project_specs=True)
    if not projects:
        return []
    release_definitions = {release_definition['name']: release_definition
                           for project in projects
                           for release_definition in
                           call(f'/{project}/_apis/release/definitions')['value']}
    if not filter_name:
        return release_definitions
    else:
        return {k: v for k, v in release_definitions.items() if fnmatch(k, filter_name)}


def main(organisations,
         projects,
         filter_name=None,
         ids=False,
         names=False,
         names_and_ids=False,
         urls=False,
         web_urls=False):
    for name, bd in list_release_definitions(organisations, projects, filter_name).items():
        output = (name, bd)
        if ids:
            output = bd['id']
        if names:
            output = bd['name']
        if names_and_ids:
            output = name, bd['id']
        if urls:
            output = bd['url']
        if web_urls:
            output = bd['_links']['web']['href']

        print(output)


def parse_args(args):
    parser = argparse.ArgumentParser(description='List TFS release definitions')
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

    parser.add_argument(
        '-fn',
        '--filter_name',
        help='Filters to definitions whose names equal this value. Append a * to filter to definitions whose names '
             'start with this value')

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        '-i', '--ids', action='store_true',
        help='Get only release definition ids')
    optional_group.add_argument(
        '-n', '--names', action='store_true',
        help='Get only release definition names')
    optional_group.add_argument(
        '-ni', '--names_and_ids', action='store_true',
        help='Get only release definition names and ids (as tuples)')
    optional_group.add_argument(
        '-u', '--urls', action='store_true',
        help='Get only release definition urls')
    optional_group.add_argument(
        '-w', '--web_urls', action='store_true',
        help='Get only release definition web urls')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
