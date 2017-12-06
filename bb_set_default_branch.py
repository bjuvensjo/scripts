#!/usr/bin/env python3

from sys import argv

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return f"projects/{project}/repos/{repo}/branches/default"


def set_default_branch(repo_specs, branch):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = '{{"id":"refs/heads/{}"}}'.format(branch)
        yield spec, call(uri, request_data, "PUT")


if __name__ == "__main__":
    dirs = ["."]
    branch = None

    if len(argv) == 1:
        print("branch is mandatory")
    elif len(argv) == 2:
        branch = argv[1]
    elif len(argv) > 2:
        branch = argv[1]
        dirs = argv[2:]

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]

    for spec, response in set_default_branch(specs, branch):
        print(f"{spec[0]}/{spec[1]}: {response}")