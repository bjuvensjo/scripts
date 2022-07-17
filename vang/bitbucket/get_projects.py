#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.api import get_all


def do_get_projects():
    return get_all("/rest/api/1.0/projects")


def get_projects(key=False):
    for project in do_get_projects():
        if key:
            print(project["key"])
        else:
            print(f'{project["key"]}: {project["name"]}')


def parse_args(args):
    parser = argparse.ArgumentParser(description="Get projects from Bitbucket")
    parser.add_argument(
        "-k", "--key", help="Print only project key", action="store_true"
    )
    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    get_projects(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
