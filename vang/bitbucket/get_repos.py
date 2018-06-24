#!/usr/bin/env python3
import argparse
import itertools
from sys import argv

from vang.bitbucket.api import call
from vang.core.core import pmap_unordered


def get_repos_page(project, limit, start):
    response = call('/rest/api/1.0/projects/{}/repos?limit={}&start={}'.format(
        project, limit, start))
    return response['size'], response['values'], response[
        'isLastPage'], response.get('nextPageStart', -1)


def get_repos(project, only_name=False, only_spec=False):
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_repos_page(
            project, limit, start)

        if size:
            for value in values:
                if only_name:
                    yield value['slug']
                elif only_spec:
                    yield (value['project']['key'], value['slug'])
                else:
                    yield value


def get_all_repos(projects, max_processes=10, only_name=False, only_spec=False):
    return itertools.chain.from_iterable(
        pmap_unordered(
            lambda p: get_repos(p, only_name, only_spec),
            projects,
            processes=max_processes))


def main(projects, name, repo_specs):
    for repo in get_all_repos(projects, only_name=name, only_spec=repo_specs):
        if repo_specs:
            print('{}/{}'.format(repo[0], repo[1]))
        else:
            print(repo)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get repos from Bitbucket')
    parser.add_argument('projects', nargs='+', help='Project keys')
    parser.add_argument(
        '-n', '--name', help='Print only repo name', action='store_true')
    parser.add_argument(
        '-r',
        '--repo_specs',
        help='Print only project_key/name',
        action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.projects, args.name, args.repo_specs)
