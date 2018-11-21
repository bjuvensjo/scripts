#!/usr/bin/env python3
import argparse
import shlex
from os import environ
from os.path import abspath
from subprocess import run
from sys import argv

from vang.bitbucket.utils import get_branch, get_project_and_repo


def open_remote(
        git_dir,
        repo=None,
        project=None,
        base_url=environ['BITBUCKET_REST_URL'],
):
    if project:
        url = f'{base_url}/projects/{project}'
    elif repo:
        p, r = repo.split('/')
        url = f'{base_url}/projects/{p}/repos/{r}/browse'
    else:
        p, r = get_project_and_repo(git_dir)
        url = ''.join([
            f'{base_url}/projects/{p}/repos/{r}/commits?',
            f'until=refs%2Fheads%2F{get_branch(git_dir)}&merges=include'
        ])
    run(shlex.split(f'open {url}'))


def main(repo_dir, repo=None, project=None):
    open_remote(abspath(f'{repo_dir}/.git'), repo, project)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Open Bitbucket url in browser')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        '--repo_dir',
        default='.',
        help='Git directory to extract repo information from')
    group.add_argument('-r', '--repo', help='Repo, e.g. key1/repo1')
    group.add_argument('-p', '--project', help='Project, e.g. key1')

    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
