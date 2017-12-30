#!/usr/bin/env python3

from sys import argv, exit

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(project, repo)


def set_default_branch(repo_specs, branch):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = '{{"id":"refs/heads/{}"}}'.format(branch)
        yield spec, call(uri, request_data, 'PUT')


if __name__ == '__main__':
    if len(argv) == 1:
        print('branch is mandatory')
        exit(1)

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in (argv[2:] if len(argv) > 2 else ['.'])]

    for spec, response in set_default_branch(specs, argv[1]):
        print('{}/{}: {}'.format(spec[0], spec[1], response))
