#!/usr/bin/env python3

from bb_api import call


def get_projects(limit, start):
    response = call('/rest/api/1.0/projects?limit={}&start={}'.format(limit, start))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_all_projects():
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_projects(limit, start)

        if size:
            for value in values:
                yield value


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get projects from Bitbucket.')
    args = parser.parse_args()

    for project in get_all_projects():
        print('{}: {}'.format(project['key'], project['name']))
