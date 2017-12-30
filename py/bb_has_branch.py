#!/usr/bin/env python3

from sys import argv

from bb_get_branches import get_branches
from bb_utils import get_clone_url, get_project_and_repo


def has_branch(repo_specs, branch):
    for spec, response in get_branches(repo_specs, branch):
        yield spec, branch in [value['displayId'] for value in response['values']]


if __name__ == '__main__':
    if len(argv) == 1:
        print('branch is mandatory')
        exit(1)

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in (argv[2:] if len(argv) > 2 else ['.'])]

    for spec, has in has_branch(specs, argv[1]):
        print('{}/{}, {}: {}'.format(spec[0], spec[1], argv[1], has))
