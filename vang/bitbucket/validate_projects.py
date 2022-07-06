#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.get_branches import get_branches
from vang.bitbucket.get_projects import get_projects
from vang.bitbucket.get_repos import get_repos
from vang.bitbucket.get_tags import get_all_tags
from vang.core.core import pmap_unordered


def validate_repos(project):
    valid = []
    corrupt = []
    for r in get_repos(project):
        s = "/".join(r)
        try:
            get_branches(r)
            get_all_tags(r)
            valid.append(s)
        except KeyError:
            corrupt.append(s)
    return valid, corrupt


def validate_projects(max_projects=None, max_processes=10):
    for valid, corrupt in pmap_unordered(
        lambda p: validate_repos(p["key"]),
        get_projects(),
        processes=max_processes,
    ):
        for v in valid:
            print(f"{v} is OK")
        for c in corrupt:
            print(f"{c} is CORRUPT")


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Validate projects by checking that the rest api can be used to retrieve repos, branches and tags."
    )
    return parser.parse_args(args)


if __name__ == "__main__":  # pragma: no cover
    validate_projects(**parse_args(argv[1:]).__dict__)
