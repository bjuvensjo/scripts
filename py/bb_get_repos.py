#!/usr/bin/env python3

from sys import argv

from bb_api import call


def get_repos(key, limit, start):
    response = call('/rest/api/1.0/projects/{}/repos?limit={}&start={}'.format(key, limit, start))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_all_repos(keys):
    for key in keys:
        limit = 25
        start = 0
        is_last_page = False

        while not is_last_page:
            size, values, is_last_page, start = get_repos(key, limit, start)

            if size:
                for value in values:
                    yield value


if __name__ == '__main__':
    for repo in get_all_repos(argv[1:]):
        print(repo)
