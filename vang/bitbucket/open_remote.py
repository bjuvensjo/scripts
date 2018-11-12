#!/usr/bin/env python3
import argparse
import shlex
import subprocess
from os import environ
from os.path import normpath
from sys import argv

from vang.bitbucket.utils import get_branch, get_project_and_repo


def open_remote(git_dir, repo=None, project=None):
    base_url = environ['BITBUCKET_REST_URL']
    if project:
        url = '{}/projects/{}'.format(base_url, project)
    elif repo:
        url = '{}/projects/{}/repos/{}/browse'.format(base_url,
                                                      *repo.split('/'))
    else:
        url = '{}/projects/{}/repos/{}/commits?until=refs%2Fheads%2F{}&merges=include'.format(
            base_url, *get_project_and_repo(git_dir), get_branch(git_dir))
    subprocess.run(shlex.split('open {}'.format(url)))


def main(repo_dir, repo=None, project=None):
    open_remote(normpath('{}/.git'.format(repo_dir)), repo, project)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Open Bitbucket url in browser')
    parser.add_argument(
        '-d',
        '--repo_dir',
        default='.',
        help='Git directory to extract repo information from')
    parser.add_argument('-r', '--repo', help='Repo, e.g. key1/repo1')
    parser.add_argument('-p', '--project', help='Project, e.g. key1')

    return parser.parse_args(args)


if __name__ == '__main__':
    main(**parse_args(argv[1:]).__dict__)
