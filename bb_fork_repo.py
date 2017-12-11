#!/usr/bin/env python3

from json import dumps
from sys import argv, exit

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return f"projects/{project}/repos/{repo}"


def fork_repo(repo_specs, fork_project):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_dict = {
            "slug": spec[1],
            "project": {
                "key": fork_project
            }
        }

        request_data = dumps(request_dict)
        yield spec, call(uri, request_data, "POST")


if __name__ == "__main__":
    dirs = ["."]
    fork_project = None

    if len(argv) == 1:
        print("fork_project is mandatory")
        exit(1)
    elif len(argv) == 2:
        fork_project = argv[1]
    elif len(argv) > 2:
        fork_project = argv[1]
        dirs = argv[2:]

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]

    for spec, response in fork_repo(specs, fork_project):
        print(f"{spec[0]}/{spec[1]}: {response}")