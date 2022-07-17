#!/usr/bin/env python3

import traceback
from argparse import ArgumentParser, BooleanOptionalAction
from itertools import count
from os import environ, makedirs
from sys import argv
from typing import Iterable, List, Tuple

from rich import print
from vang.azdo.list_projects import do_list_projects
from vang.azdo.list_repos import do_list_repos
from vang.pio.shell import run_commands


def clone(commands, root_dir):
    makedirs(root_dir, exist_ok=True)
    yield from run_commands(
        [(cmd, root_dir) for cmd in commands], max_processes=5, timeout=180, check=False
    )


def get_commands(clone_specs, branch, flat):
    b = f" -b {branch}" if branch else ""
    return [f'git clone {c[0]}{b}{"" if flat else f" {c[1]}"}' for c in clone_specs]


def get_clone_specs(
    azure_devops_url: str,
    token: str,
    projects: Iterable,
    flat: bool,
    verify_certificate: bool,
) -> List[Tuple]:
    return [
        (r["remoteUrl"], r["name"] if flat else f'{r["project"]["name"]}/{r["name"]}')
        for p in projects
        for r in do_list_repos(
            azure_devops_url,
            token,
            *p.split("/"),
            verify_certificate=verify_certificate,
        )["value"]
    ]


def do_clone_repos(
    azure_devops_url: str,
    token: str,
    clone_dir: str,
    organisation: str = None,
    projects: List[str] = None,
    repos: List[str] = None,
    branch: str = None,
    flat: bool = True,
    verify_certificate: bool = True,
) -> List[Tuple]:
    if organisation:
        projects = do_list_projects(
            azure_devops_url,
            token,
            organisation,
            names=False,
            project_specs=True,
            verify_certificate=verify_certificate,
        )
    elif repos:
        projects = set(["/".join(r.split("/")[:2]) for r in repos])

    clone_specs = get_clone_specs(
        azure_devops_url, token, projects, flat, verify_certificate
    )

    if repos:
        clone_dirs = [
            r.split("/")[2] if flat else "/".join(r.split("/")[1:]) for r in repos
        ]
        clone_specs = [
            (url, clone_dir)
            for url, clone_dir in clone_specs
            if clone_dir in clone_dirs
        ]

    commands = get_commands(clone_specs, branch, flat)
    for n, process in zip(count(1), clone(commands, clone_dir)):
        try:
            print(str(n).zfill(2), process.stdout.decode("utf-8"), end="")
        except OSError:  # pragma: no cover
            print(traceback.format_exc())

    return clone_specs


def parse_args(args):
    parser = ArgumentParser(description="Clone Azure DevOps repos")
    parser.add_argument(
        "-au",
        "--azure_devops_url",
        default="https://dev.azure.com",
        help="The Azure DevOps REST API base url",
    )
    parser.add_argument(
        "--verify_certificate",
        default=True,
        action=BooleanOptionalAction,
        help="If certificate of Azure should be verified",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=environ.get("AZDO_TOKEN", ""),
        help="The Azure DevOps authorisation token",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-o", "--organisation", help="Azure DevOps organisation, e.g organisation"
    )
    group.add_argument(
        "-p",
        "--projects",
        nargs="+",
        help="Azure DevOps projects, e.g organisation/project",
    )
    group.add_argument(
        "-r", "--repos", nargs="+", help="Repos, e.g. organisation/project/repo"
    )
    parser.add_argument("-b", "--branch", help="The clone branch")
    parser.add_argument(
        "-d", "--clone_dir", default=".", help="The directory to clone into"
    )
    parser.add_argument(
        "-f", "--flat", help="Clone to flat structure", action="store_true"
    )
    return parser.parse_args(args)


def clone_repos(
    azure_devops_url: str,
    token: str,
    clone_dir: str,
    organisation: str,
    projects: List[str],
    repos: List[str],
    branch: str,
    flat: bool,
    verify_certificate: bool,
):
    for a_repo in do_clone_repos(
        azure_devops_url,
        token,
        clone_dir,
        organisation,
        projects,
        repos,
        branch,
        flat,
        verify_certificate,
    ):
        print(a_repo[1])


def main() -> None:  # pragma: no cover
    clone_repos(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
