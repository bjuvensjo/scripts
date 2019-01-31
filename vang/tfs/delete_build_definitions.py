#!/usr/bin/env python3
import argparse
from sys import argv

from vang.tfs.api import call


def delete_build_definition(project, definition_id):
    organisation, project = project.split('/')
    return call(
        f'/{organisation}/{project}/_apis/build/definitions/{definition_id}?api-version=3.2',
        method='DELETE',
        only_response_code=True
    )


def main(project, definition_ids):
    for definition_id in definition_ids:
        response_code = delete_build_definition(project, definition_id)
        print(definition_id, response_code)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Delete TFS build definitions')
    parser.add_argument(
        'project',
        help='TFS projects, e.g organisation/project')
    parser.add_argument(
        'definition_ids',
        nargs='+',
        help='The TFS build definitions id, e.g. 1234')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
