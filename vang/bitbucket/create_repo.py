#!/usr/bin/env python3

import argparse
from os import name, system
from sys import argv

from vang.bitbucket.api import call


def create_repo(project, repo):
    uri = f'/rest/api/1.0/projects/{project}/repos'
    # request_data = f'{{"name":"{repo}","scmId":"git","forkable":true}}'
    request_data = {'name': repo, 'scmId': 'git', 'forkable': True}
    return call(uri, request_data, 'POST')


def main(project, repository):
    response = create_repo(project, repository)
    commands = '    git remote add origin ' \
        f'{response["links"]["clone"][0]["href"]}\n' \
               '    git push -u origin develop'
    print('If you already have code ready to be pushed to this repository '
          'then run this in your terminal.')
    print(commands)
    if name == 'posix':
        system(f'echo "{commands}\\c" | pbcopy')
        print('(The commands are copied to the clipboard)')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create Bitbucket repository')
    parser.add_argument('project', help='Project key')
    parser.add_argument('repository', help='Repository')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
