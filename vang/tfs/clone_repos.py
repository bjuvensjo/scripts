#!/usr/bin/env python3

import argparse
import traceback
from itertools import count
from os import makedirs
from sys import argv

from vang.pio.shell import run_commands
from vang.tfs.get_repos import get_repos


def clone(commands, root_dir):
    makedirs(root_dir, exist_ok=True)
    yield from run_commands([(cmd, root_dir) for cmd in commands],
                            max_processes=5,
                            timeout=60,
                            check=False)


def get_commands(clone_specs, branch, flat):
    b = f' -b {branch}' if branch else ''
    return [
        f'git clone {c[0]}{b}{"" if flat else f" {c[1]}"}' for c in clone_specs
    ]


def get_clone_specs(projects):
    return [(repo['remoteUrl'], f'{organisation}/{project}/{repo["name"]}')
            for organisation, project in [p.split('/') for p in projects]
            for repo in get_repos(organisation, project)]


def clone_repos(root_dir,
                organisations=None,
                projects=None,
                repos=None,
                branch=None,
                flat=False):
    if organisations:
        print('Not yet supported')
        return []
    if projects:
        clone_specs = get_clone_specs(projects)
    if repos:
        clone_specs = [
            spec for spec in get_clone_specs(
                set(['/'.join(r.split('/')[:2]) for r in repos]))
            if spec[1] in repos
        ]

    commands = get_commands(clone_specs, branch, flat)
    for n, process in zip(count(1), clone(commands, root_dir)):
        try:
            print(str(n).zfill(2), process.stdout.decode(), end='')
        except OSError:
            print(traceback.format_exc())

    return commands


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
        help='Repos, e.g. organisation/project/repo1')
    parser.add_argument('-b', '--branch', help='The clone branch')
    parser.add_argument(
        '-d', '--dir', default='.', help='The directory to clone into')
    parser.add_argument(
        '-f', '--flat', help='Clone to flat structure', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])

    clone_repos(args.dir, args.organisations, args.projects, args.repos,
                args.branch, args.flat)
