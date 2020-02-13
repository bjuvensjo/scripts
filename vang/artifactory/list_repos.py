#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.artifactory import api


def list_repos(repo_type=None, only_key=False, only_url=False):
    result = api.call('/api/repositories')
    if repo_type:
        result = [r for r in result if r['type'] == repo_type]
    if only_key:
        result = [r['key'] for r in result]
    if only_url:
        result = [r['url'] for r in result]
    return result


def main(repo_type, only_key, only_url):
    for repo in list_repos(repo_type, only_key, only_url):
        print(repo)


def parse_args(args):
    parser = ArgumentParser(
        description='List repositories in Artifactory')
    parser.add_argument(
        '-t',
        '--repo_type',
        default=None,
        help='Repository type, e.g. LOCAL, REMOTE, VIRTUAL. Default is all.')
    parser.add_argument('-k', '--only_key', help='Print only repo key', action='store_true')
    parser.add_argument('-u', '--only_url', help='Print only repo url', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
