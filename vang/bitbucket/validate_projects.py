#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.get_branches import do_get_branches
from vang.bitbucket.get_projects import do_get_projects
from vang.bitbucket.get_repos import do_get_repos
from vang.bitbucket.get_tags import get_all_tags
from vang.core.core import pmap_unordered


def validate_repos(project):
    valid = []
    corrupt = []
    for r in do_get_repos(project):
        s = "/".join(r)
        try:
            do_get_branches(r)
            get_all_tags(r)
            valid.append(s)
        except KeyError:
            corrupt.append(s)
    return valid, corrupt


def validate_projects(max_processes=10):
    for valid, corrupt in pmap_unordered(
        lambda p: validate_repos(p["key"]),
        do_get_projects(),
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


def main() -> None:  # pragma: no cover
    validate_projects(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
