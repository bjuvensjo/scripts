#!/usr/bin/env python3

import argparse
import traceback
from itertools import count
from os import makedirs
from sys import argv

from vang.pio.shell import run_commands
from vang.tfs.get_projects import get_projects
from vang.tfs.get_repos import get_repos


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


def get_clone_specs(projects, flat):
    return [(repo[1]['remoteUrl'],
             repo[1]['name'] if flat else f'{repo[0]}/{repo[1]["name"]}')
            for repo in get_repos(projects=projects)]


def clone_repos(root_dir,
                organisations=None,
                projects=None,
                repos=None,
                branch=None,
                flat=False):
    if organisations:
        projects = get_projects(organisations, project_specs=True)
    elif repos:
        projects = set(['/'.join(r.split('/')[:2]) for r in repos])

    clone_specs = get_clone_specs(projects, flat)

    if repos:
        clone_dirs = [r.split('/')[2] if flat else r for r in repos]
        clone_specs = [(url, clone_dir) for url, clone_dir in clone_specs
                       if clone_dir in clone_dirs]

    commands = get_commands(clone_specs, branch, flat)
    for n, process in zip(count(1), clone(commands, root_dir)):
        try:
            print(str(n).zfill(2), process.stdout.decode(), end='')
        except OSError:  # pragma: no cover
            print(traceback.format_exc())

    return clone_specs


def parse_args(args):
    parser = argparse.ArgumentParser(description='Clone TFS repos')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-o',
        '--organisations',
        nargs='+',
        help='TFS organisations, e.g organisation')
    group.add_argument(
        '-p',
        '--projects',
        nargs='+',
        help='TFS projects, e.g organisation/project')
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


def main(clone_dir, organisations, projects, repos, branch, flat):
    for a_repo in clone_repos(
            clone_dir,
            organisations,
            projects,
            repos,
            branch,
            flat,
    ):
        print(a_repo[1])


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
