#!/usr/bin/env python3

from sys import argv

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}/branches/default'.format(project, repo)


def get_default_branch(repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        yield spec, call(uri)


if __name__ == '__main__':
    specs = [get_project_and_repo(get_clone_url(dir)) for dir in (argv[1:] if len(argv) > 1 else ['.'])]

    for spec, response in get_default_branch(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], response['displayId']))
