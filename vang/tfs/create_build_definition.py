#!/usr/bin/env python3
import argparse
from sys import argv

from vang.tfs.api import call
from vang.tfs.definition_utils import get_definition, get_definition_name


def get_build_definition(template, organisation, project, repo, branch, comment=None):
    return get_definition(template,
                          {
                              'name': get_definition_name(project, repo, branch),
                              'organisation': organisation,
                              'project': project,
                              'repo': repo,
                              'branch': branch
                          },
                          {'comment': comment} if comment else {})


def create_build_definition(organisation, project, build_definition):
    return call(
        # f'/{organisation}/{project}/_apis/build/definitions?api-version=3.2',
        f'/{organisation}/{project}/_apis/build/definitions?api-version=3.2',
        request_data=build_definition,
        method='POST',
        only_response_code=True
    )


def main(project, repo, branch, template, comment=None):
    organisation, project = project.split('/')
    response = create_build_definition(organisation, project,
                                       get_build_definition(template, organisation, project, repo, branch, comment))
    print(response)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create TFS build definitions')
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
