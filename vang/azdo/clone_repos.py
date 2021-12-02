#!/usr/bin/env python3

import argparse
import traceback
from itertools import count
from os import makedirs, environ
from sys import argv
from typing import List, Iterable, Tuple

from vang.azdo.list_projects import list_projects
from vang.azdo.list_repos import list_repos
from vang.pio.shell import run_commands


def clone(commands, root_dir):
    makedirs(root_dir, exist_ok=True)
    yield from run_commands([(cmd, root_dir) for cmd in commands],
                            max_processes=5,
                            timeout=180,
                            check=False)


def get_commands(clone_specs, branch, flat):
    b = f' -b {branch}' if branch else ''
    return [
        f'git clone {c[0]}{b}{"" if flat else f" {c[1]}"}' for c in clone_specs
    ]


def get_clone_specs(token: str, projects: Iterable, flat: bool) -> List[Tuple]:
    return [(r['remoteUrl'],
             r['name'] if flat else f'{r["project"]["name"]}/{r["name"]}')
            for p in projects
            for r in list_repos(token, *p.split('/'))['value']]


def clone_repos(token: str, clone_dir: str, organisation: str = None, projects: List[str] = None,
                repos: List[str] = None, branch: str = None, flat: bool = True) -> List[Tuple]:
    if organisation:
        projects = list_projects(token, organisation, names=False, project_specs=True)
    elif repos:
        projects = set(['/'.join(r.split('/')[:2]) for r in repos])

    clone_specs = get_clone_specs(token, projects, flat)

    if repos:
        clone_dirs = [r.split('/')[2] if flat else '/'.join(r.split('/')[1:]) for r in repos]
        clone_specs = [(url, clone_dir) for url, clone_dir in clone_specs
                       if clone_dir in clone_dirs]

    commands = get_commands(clone_specs, branch, flat)
    for n, process in zip(count(1), clone(commands, clone_dir)):
        try:
            print(str(n).zfill(2), process.stdout.decode(), end='')
        except OSError:  # pragma: no cover
            print(traceback.format_exc())

    return clone_specs


def parse_args(args):
    parser = argparse.ArgumentParser(description='Clone Azure DevOps repos')
    parser.add_argument(
        '--token',
        default=environ.get('AZDO_TOKEN', ''),
        help='The Azure DevOps authorisation token')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-o',
        '--organisation',
        help='Azure DevOps organisation, e.g organisation')
    group.add_argument(
        '-p',
        '--projects',
        nargs='+',
        help='Azure DevOps projects, e.g organisation/project')
    group.add_argument(
        '-r',
        '--repos',
        nargs='+',
        help='Repos, e.g. organisation/project/repo')
    parser.add_argument('-b', '--branch', help='The clone branch')
    parser.add_argument(
        '-d', '--clone_dir', default='.', help='The directory to clone into')
    parser.add_argument(
        '-f', '--flat', help='Clone to flat structure', action='store_true')
    return parser.parse_args(args)


def main(token: str, clone_dir: str, organisation: str, projects: List[str], repos: List[str], branch: str, flat: bool):
    for a_repo in clone_repos(
            token,
            clone_dir,
            organisation,
            projects,
            repos,
            branch,
            flat,
    ):
        print(a_repo[1])


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
