#!/usr/bin/env python3
import itertools
from multiprocessing.dummy import Pool

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def get_tags_page(spec, tag, limit, start, order_by='MODIFICATION'):
    response = call(
        '/rest/api/1.0/projects/{}/repos/{}/tags?filterText={}&limit={}&start={}&orderBy'.format(spec[0], spec[1], tag, limit,
                                                                                         start, order_by))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_all_tags(spec, tag=''):
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_tags_page(spec, tag, limit, start)

        if size:
            for value in values:
                yield spec, value


def get_tags(specs, tag='', max_processes=10):
    with Pool(processes=max_processes) as pool:
        return itertools.chain.from_iterable(pool.map(lambda s: get_all_tags(s, tag), specs))


def main(tag='', name=False, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in get_tags(specs, tag):
        if name:
            print(response['displayId'])
        else:
            print('{}/{}: {}'.format(spec[0], spec[1], response['displayId']))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get repository tags from Bitbucket')
    parser.add_argument('-t', '--tag',
                        help='Tag filter',
                        default='')
    parser.add_argument('-n', '--name',
                        help='Print only tag name',
                        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.tag, args.name, args.dirs, args.repos, args.projects)
