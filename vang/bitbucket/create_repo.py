#!/usr/bin/env python3

import argparse
from os import name, system
from sys import argv

from vang.bitbucket.api import call


def create_repo(project, repo):
    uri = '/rest/api/1.0/projects/{}/repos'.format(project)
    request_data = '{{"name":"{}","scmId":"git","forkable":true}}'.format(repo)
    return call(uri, request_data, 'POST')


def main(project, repository):
    response = create_repo(project, repository)
    commands = '    git remote add origin {}\n' \
               '    git push -u origin develop'.format(response['links']['clone'][0]['href'])
    print('If you already have code ready to be pushed to this repository '
          'then run this in your terminal.')
    print(commands)
    if name == 'posix':
        system('echo "{}\c" | pbcopy'.format(commands))
        print('(The commands are copied to the clipboard)')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Create Bitbucket repository')
    parser.add_argument('project', help='Project key')
    parser.add_argument('repository', help='Repository')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.project, args.repository)
