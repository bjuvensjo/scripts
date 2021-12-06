#!/usr/bin/env python3
import argparse
import itertools
from multiprocessing.dummy import Pool
from sys import argv

from vang.bitbucket.api import get_all
from vang.bitbucket.utils import get_repo_specs


# def get_tags_page(spec, tag, limit, start, order_by='MODIFICATION'):
#     response = call(
#         f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/tags?'
#         f'filterText={tag}&limit={limit}&start={start}&orderBy={order_by}')
#     return response['size'], response['values'], response[
#         'isLastPage'], response.get('nextPageStart', -1)


def get_all_tags(spec, tag='', order_by='MODIFICATION'):
    for t in get_all(f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/tags',
                     {'filterText': tag, 'orderBy': order_by} if tag else {'orderBy': order_by}):
        yield spec, t
    # limit = 25
    # start = 0
    # is_last_page = False
    #
    # while not is_last_page:
    #     size, values, is_last_page, start = get_tags_page(
    #         spec, tag, limit, start)
    #
    #     if size:
    #         for value in values:
    #             yield spec, value


def get_tags(specs, tag='', max_processes=10):
    with Pool(processes=max_processes) as pool:
        return itertools.chain.from_iterable(
            pool.map(lambda s: get_all_tags(s, tag), specs))


def main(tag='', name=False, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in get_tags(specs, tag):
        if name:
            print(response['displayId'])
        else:
            print(f'{spec[0]}/{spec[1]}: {response["displayId"]}')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get repository tags from Bitbucket')
    parser.add_argument('-t', '--tag', help='Tag filter', default='')
    parser.add_argument(
        '-n', '--name', help='Print only tag name', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        '--dirs',
        nargs='*',
        default=['.'],
        help='Git directories to extract repo information from')
    group.add_argument(
        '-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument(
        '-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
