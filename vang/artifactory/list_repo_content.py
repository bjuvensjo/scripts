#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.artifactory.api import call


def get_repo_content(repo_key):
    return call(f"/api/storage/{repo_key}?list&deep=1&listFolders=1")


def do_list_repo_content(repo_key, only_files=True):
    result = get_repo_content(repo_key)
    result = result["files"]
    if only_files:
        result = [f["uri"] for f in result if not f["folder"]]
    return result


def list_repo_content(repo_key, only_files):
    for f in do_list_repo_content(repo_key, only_files):
        print(f)


def parse_args(args):
    parser = ArgumentParser(description="List repository content")
    parser.add_argument("repo_key", help="Repository key, e.g. libs-release")
    parser.add_argument(
        "-f",
        "--only_files",
        help="Print only ordinary files, i.e. not directories",
        action="store_true",
    )
    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    list_repo_content(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
