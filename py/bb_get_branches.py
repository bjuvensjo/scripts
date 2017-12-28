#!/usr/bin/env python3

from sys import argv

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo, branch):
    return '/rest/api/1.0/projects/{}/repos/{}/branches?filterText={}'.format(project, repo, branch)


def get_branches(repo_specs, branch=''):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1], branch)
        yield spec, call(uri)


if __name__ == '__main__':
    dirs = ['.']
    branch = ''

    if len(argv) == 2:
        branch = argv[1]
    elif len(argv) > 2:
        branch = argv[1]
        dirs = argv[2:]

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]

    for spec, response in get_branches(specs, branch):
        print('{}/{}: {}'.format(spec[0], spec[1], [value['displayId'] for value in response['values']]))
