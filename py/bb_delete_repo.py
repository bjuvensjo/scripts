#!/usr/bin/env python3
from os.path import basename
from sys import argv

from bb_api import call
from bb_utils import get_project_and_repo, get_clone_url


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}'.format(projectKey=project, repositorySlug=repo)


def delete_repo(repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        yield spec, call(uri, method="DELETE")


if __name__ == '__main__':
    if '-d' in argv and len(argv) > 1:
        dirs = ['.'] if len(argv) == 2 else [arg for arg in argv[1:] if arg != '-d']        
        specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]
    elif len(argv) == 3:
        specs = [[argv[1], argv[2]]]
    else:
        print('Usage: {} [-d dirs] | [project repo]'.format(basename(__file__)))
        exit(1)

    for spec, response in delete_repo(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], response))
