#!/usr/bin/env python3
import argparse
from sys import argv

from vang.tfs.api import call_url
from vang.tfs.definition_utils import get_definition, get_definition_name
from vang.tfs.list_release_definitions import list_release_definitions


def get_current_definition(organisation, project, definition_name):
    return list_release_definitions(projects=(f'{organisation}/{project}',), filter_name=definition_name)[
        definition_name]


def get_release_definition(template, organisation, project, repo, branch, definition_name, definition_id, revision,
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


def update_release_definition(definition_url, release_definition):
    return call_url(
        f'{definition_url}?api-version=3.2-preview',
        request_data=release_definition,
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
    response = update_release_definition(definition_url,
                                         get_release_definition(template, organisation, project, repo,
                                                                branch, definition_name, definition_id, revision,
                                                                comment))
    print(response)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Update TFS release definitions')
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
        help='The TFS release definition template file, e.g. release_definition_template.json')
    parser.add_argument(
        '-c',
        '--comment',
        help='The comment to add to the release definition, e.g. a commit sha of the release definition template')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
