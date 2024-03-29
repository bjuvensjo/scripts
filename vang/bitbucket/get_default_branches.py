#!/usr/bin/env python3
import argparse
from multiprocessing.dummy import Pool
from sys import argv

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def get_repo_default_branch(spec):
    return spec, call(
        f"/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/branches/default"
    )


def get_default_branch(repo_specs, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.map(get_repo_default_branch, repo_specs)


def get_default_branches(dirs, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in get_default_branch(specs):
        print(f'{spec[0]}/{spec[1]}: {response["displayId"]}')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Get default repository branches from Bitbucket"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--dirs",
        nargs="*",
        default=["."],
        help="Git directories to extract repo information from",
    )
    group.add_argument(
        "-r", "--repos", nargs="*", help="Repos, e.g. key1/repo1 key2/repo2"
    )
    group.add_argument("-p", "--projects", nargs="*", help="Projects, e.g. key1 key2")
    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    get_default_branches(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
