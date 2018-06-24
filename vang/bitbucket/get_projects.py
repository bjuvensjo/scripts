#!/usr/bin/env python3

from vang.bitbucket.api import call


def get_projects_page(limit, start):
    response = call('/rest/api/1.0/projects?limit={}&start={}'.format(limit, start))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_projects():
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_projects_page(limit, start)

        if size:
            for value in values:
                yield value


def main(only_key=False):
    for project in get_projects():
        if only_key:
            print(project['key'])
        else:
            print('{}: {}'.format(project['key'], project['name']))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get projects from Bitbucket')
    parser.add_argument('-k', '--key',
                        help='Print only project key',
                        action='store_true')
    args = parser.parse_args()

    main(args.key)
