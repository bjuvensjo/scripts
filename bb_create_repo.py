#!/usr/bin/env python3

from os import name, system
from sys import argv

from bb_api import call


def _get_uri(project):
    return f"projects/{project}/repos"


def create_repo(project, repo):
    uri = _get_uri(project)
    request_data = '{{"name":"{}","scmId":"git","forkable":true}}'.format(repo).encode('UTF-8')
    return call(uri, request_data, "POST")


if __name__ == "__main__":
    dirs = ["."]
    branch = None

    if len(argv) != 3:
        print("project key and repo name is mandatory")
    else:
        project = argv[1]
        repo = argv[2]
        response = create_repo(project, repo)
        commands = f"    git remote add origin {response['links']['clone'][0]['href']}\n    git push -u origin develop"

        print("If you already have code ready to be pushed to this repository then run this in your terminal.")
        print(commands)

        if name == 'posix':
            system(f"echo '{commands}\c' | pbcopy")
            print("(The commands are copied to the clipboard)")
