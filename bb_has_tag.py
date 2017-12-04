#!/usr/bin/env python3

from sys import argv

from bb_get_tags import get_tags
from bb_utils import get_clone_url, get_project_and_repo


def has_tag(repo_specs, tag):
    for spec, response in get_tags(repo_specs, tag):
        yield spec, tag in [value['displayId'] for value in response['values']]


if __name__ == "__main__":
    dirs = ["."]
    tag = None

    if len(argv) == 1:
        print("tag is mandatory")
    elif len(argv) == 2:
        tag = argv[1]
    elif len(argv) > 2:
        tag = argv[1]
        dirs = argv[2:]

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]

    for spec, has in has_tag(specs, tag):
        print(f"{spec[0]}/{spec[1]}: {has}")
