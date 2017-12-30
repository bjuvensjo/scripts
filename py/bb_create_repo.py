#!/usr/bin/env python3

from os import name, system
from os.path import basename

from sys import argv

from bb_api import call


def _get_uri(project):
    return '/rest/api/1.0/projects/{}/repos'.format(project)


def create_repo(project, repo):
    uri = _get_uri(project)
    request_data = '{{"name":"{}","scmId":"git","forkable":true}}'.format(repo)
    return call(uri, request_data, "POST")


if __name__ == '__main__':
    if len(argv) != 3:
        print('Usage: {} project repo [clone_dirs]'.format(basename(__file__)))
        exit(1)
    else:
        project = argv[1]
        repo = argv[2]
        response = create_repo(project, repo)
        commands = '    git remote add origin {}\n' \
                   '    git push -u origin develop'.format(response['links']['clone'][0]['href'])

        print('If you already have code ready to be pushed to this repository then run this in your terminal.')
        print(commands)

        if name == 'posix':
            system(f"echo '{commands}\c' | pbcopy")
            print("(The commands are copied to the clipboard)")
