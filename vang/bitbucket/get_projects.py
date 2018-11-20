#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.api import call


def get_projects_page(limit, start):
    response = call(f'/rest/api/1.0/projects?limit={limit}&start={start}')
    return response['size'], response['values'], response[
        'isLastPage'], response.get('nextPageStart', -1)


def get_projects():
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_projects_page(limit, start)

        if size:
            for value in values:
                yield value


def main(key=False):
    for project in get_projects():
        if key:
            print(project['key'])
        else:
            print(f'{project["key"]}: {project["name"]}')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Get projects from Bitbucket')
    parser.add_argument(
        '-k', '--key', help='Print only project key', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
