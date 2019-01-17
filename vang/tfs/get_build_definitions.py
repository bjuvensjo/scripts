#!/usr/bin/env python3

import argparse
from sys import argv

from vang.tfs.api import call
from vang.tfs.get_projects import get_projects


def get_build_definitions(organisations=None,
                          projects=None,
                          names=False,
                          urls=False,
                          web_urls=False):
    if organisations:
        projects = get_projects(organisations, project_specs=True)
    if not projects:
        return []
    build_definitions = [(project, repo)
                         for project in projects
                         for repo in
                         call(f'/{project}/_apis/build/definitions')['value']]
    if names:
        return [repo[1]['name'] for repo in build_definitions]
    if urls:
        return [repo[1]['url'] for repo in build_definitions]
    if web_urls:
        return [repo[1]['_links']['web']['href'] for repo in build_definitions]

    return build_definitions


def main(organisations, projects, names, urls, web_urls):
    for repo in get_build_definitions(organisations, projects, names, urls,
                                      web_urls):
        print(repo)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get TFS build definitions')
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
        '-n', '--names', action='store_true',
        help='Get only build definition names')
    optional_group.add_argument(
        '-u', '--urls', action='store_true',
        help='Get only build definition urls')
    optional_group.add_argument(
        '-w', '--web_urls', action='store_true',
        help='Get only build definition web urls')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
