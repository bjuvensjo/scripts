#!/usr/bin/env python3
import argparse
from json import dumps
from sys import argv

from vang.tfs.api import call
from vang.tfs.definition_utils import get_definition, get_definition_name


def get_release_definition(template, project, repo, branch, comment=None):
    return get_definition(template,
                          {
                              'name': get_definition_name(project, repo, branch),
                              'project': project,
                              'branch': branch
                          },
                          {'comment': comment} if comment else {})


def create_release_definition(organisation, project, release_definition):
    return call(
        f'/{organisation}/{project}/_apis/release/definitions?api-version=3.2-preview',
        request_data=release_definition,
        method='POST',
        only_response_code=True
    )


def main(project, repo, branch, template, comment=None):
    organisation, project = project.split('/')
    x = get_release_definition(template, project, repo, branch, comment)
    print(dumps(x, indent=4))
    response = create_release_definition(organisation, project,
                                         get_release_definition(template, project, repo, branch, comment))
    print(response)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create TFS release definitions')
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
