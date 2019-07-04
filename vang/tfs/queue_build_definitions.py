#!/usr/bin/env python3

import argparse
import re
from json import dumps
from sys import argv

from vang.tfs.api import call_url
from vang.tfs.list_build_definitions import list_build_definitions


def queue_build_definitions(organisations=None,
                            projects=None,
                            filter_name=None, ):
    name_and_urls = [(name, bd['id'], bd['url']) for name, bd in
                     list_build_definitions(organisations, projects, filter_name).items()]
    for name, definition_id, url in name_and_urls:
        build_url = re.sub(r'_apis/.*', '', url) + '_apis/build/builds?api-version=3.2'
        yield name, call_url(build_url, {'definition': {'id': definition_id}}, method='POST')


def main(organisations,
         projects,
         filter_name=None,
         format_output=False):
    for name, result in queue_build_definitions(organisations, projects, filter_name):
        json = dumps(result, indent=4) if format_output else dumps(result)
        print(json)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Queue TFS build definitions')
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
        '-f', '--format_output', action='store_true',
        help='Format output')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
