#!/usr/bin/env python3

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
        print(argv[1:])
        project = argv[1]
        repo = argv[2]
        response = create_repo(project, repo)
        print(f"{project}/{repo}: {response}")
