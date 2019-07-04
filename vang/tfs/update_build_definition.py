#!/usr/bin/env python3
import argparse
from json import dumps
from pprint import pprint
from sys import argv

from vang.tfs.api import call_url
from vang.tfs.definition_utils import get_definition, get_definition_name
from vang.tfs.list_build_definitions import list_build_definitions


def get_current_definition(organisation, project, definition_name):
    return list_build_definitions(projects=(f'{organisation}/{project}',), filter_name=definition_name)[definition_name]


def get_build_definition(template, organisation, project, repo, branch, definition_name, definition_id, revision,
                         comment=None):
    additions = {'id': definition_id, 'revision': revision}
    if comment:
        additions['comment'] = comment
    return get_definition(template,
                          {
                              'name': definition_name,
                              'organisation': organisation,
                              'project': project,
                              'repo': repo,
                              'branch': branch
                          },
                          additions)


def update_build_definition(definition_url, build_definition):
    return call_url(
        f'{definition_url}&api-version=3.2',
        request_data=build_definition,
        method='PUT',
        only_response_code=True
    )


def main(project, repo, branch, template, comment=None):
    organisation, project = project.split('/')
    definition_name = get_definition_name(project, repo, branch)
    definition = get_current_definition(organisation, project, definition_name)
    definition_url = definition['url']
    definition_id = definition['id']
    revision = definition['revision']

    print(dumps(get_build_definition(template, organisation, project, repo,
                                      branch, definition_name, definition_id, revision, comment)))

    response = update_build_definition(definition_url,
                                       get_build_definition(template, organisation, project, repo,
                                                            branch, definition_name, definition_id, revision, comment))
    print(response)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Update TFS build definitions')
    parser.add_argument(
        'project',
        help='TFS projects, e.g organisation/project')
    parser.add_argument(
        'repo',
        help='The TFS git repo name, e.g. spam.eggs')
    parser.add_argument(
        'branch',
        help='The TFS git repo branch, e.g. 1.0.x')
    parser.add_argument(
        'template',
        help='The TFS build definition template file, e.g. build_definition_template.json')
    parser.add_argument(
        '-c',
        '--comment',
        help='The comment to add to the build definition, e.g. a commit sha of the build definition template')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
