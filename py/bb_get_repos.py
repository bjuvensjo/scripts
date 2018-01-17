#!/usr/bin/env python3
from multiprocessing.dummy import Pool

import itertools

from bb_api import call


def get_repos_page(key, limit, start):
    response = call('/rest/api/1.0/projects/{}/repos?limit={}&start={}'.format(key, limit, start))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_repos(key):
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_repos_page(key, limit, start)

        if size:
            for value in values:
                yield value


def get_all_repos(keys, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return itertools.chain.from_iterable(pool.map(get_repos, keys))


def main(keys, name, project):
    for repo in get_all_repos(keys):
        if name:
            print(repo['slug'])
        elif project:
            print('{}/{}'.format(repo['project']['key'], repo['slug']))
        else:
            print(repo)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Prints repos of specified project keys')
    parser.add_argument('keys', nargs='+', help='Project keys')
    parser.add_argument('-n', '--name',
                        help='Print only repo name',
                        action='store_true')
    parser.add_argument('-p', '--project',
                        help='Print only project_key/name',
                        action='store_true')
    args = parser.parse_args()

    main(args.keys, args.name, args.project)
