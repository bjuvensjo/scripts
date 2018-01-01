#!/usr/bin/env python3

from json import dumps
from os.path import basename
from sys import argv, exit

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}'.format(project, repo)


def fork_repo(repo_specs, fork_project):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_dict = {
            'slug': spec[1],
            'project': {
                'key': fork_project
            }
        }

        request_data = dumps(request_dict)
        yield spec, call(uri, request_data, 'POST')


if __name__ == '__main__':
    if '-d' in argv and len(argv) > 2:
        stripped_argv = [arg for arg in argv if arg != '-d']
        fork_project = stripped_argv[1]
        dirs = ['.'] if len(stripped_argv) == 1 else [arg for arg in stripped_argv[1:] if arg != '-d']
        specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]
    elif len(argv) == 4:
        fork_project = argv[1]
        specs = [[argv[2], argv[3]]]
    else:
        print('Usage: {} fork_project [-d dirs] | [project repo]'.format(basename(__file__)))
        exit(1)

    for spec, response in fork_repo(specs, fork_project):
        print('{}/{}: {}'.format(spec[0], spec[1], response))
