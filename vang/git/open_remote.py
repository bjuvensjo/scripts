#!/usr/bin/env python3
import argparse
import re
import shlex
from os.path import abspath
from subprocess import run, CalledProcessError
from sys import argv

from vang.pio.shell import run_command


def get_origin_remote_url(repo_dir, remote):
    command = 'git remote -v'
    try:
        rc, output = run_command(command, True, repo_dir)
        for line in output.split('\n'):
            if remote in line:
                return re.split(r'[\t ]+', line)[1]
    except CalledProcessError as cpe:
        print(cpe)
    return None


def open_remote(repo_dir, remote):
    url = get_origin_remote_url(repo_dir, remote)
    if url:
        print(f'Opening {url}')
        run(shlex.split(f'open {url}'))
    else:
        print(f'Found no url to open in {repo_dir}')


def main(repo_dir, remote):  # pragma: no cover
    open_remote(abspath(repo_dir), remote)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Open remote url in browser')
    parser.add_argument(
        '-d',
        '--repo_dir',
        default='.',
        help='Git directory to extract repo information from')
    parser.add_argument(
        '-r',
        '--remote',
        default='origin',
        help='The remote to open')

    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
