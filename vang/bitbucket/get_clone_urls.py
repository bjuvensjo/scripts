#!/usr/bin/env python3
import argparse
from os.path import normpath
from sys import argv

from vang.bitbucket.get_repos import get_all_repos


def get_clone_urls(keys, command=False, branch=False, flat=False):
    for repo in get_all_repos(keys):
        project, repo, clone_url = repo['project']['key'], repo['slug'], repo[
            'links']['clone'][0]['href']
        if command:
            clone_dir = normpath('{}/{}'.format(
                project, repo if flat else repo.replace('.', '/')))
            if branch:
                clone_command = 'git clone -b {} {} {}'.format(
                    branch, clone_url, clone_dir)
            else:
                clone_command = 'git clone {} {}'.format(clone_url, clone_dir)
            yield clone_dir, project, repo, clone_command
        else:
            yield None, project, repo, clone_url


def main(projects, command, branch):
    for clone_dir, project, repo, clone_url in get_clone_urls(
            projects, command, branch):
        print(clone_url)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get clone urls for projects from Bitbucket.')
    parser.add_argument('projects', nargs='+', help='The projects.')
    parser.add_argument(
        '-c', '--command', help='Print as clone commands', action='store_true')
    parser.add_argument(
        '-b', '--branch', help='Add -b <branch> to clone commands')
    return parser.parse_args(args)


if __name__ == '__main__':
    main(**parse_args(argv[1:]).__dict__)
