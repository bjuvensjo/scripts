#!/usr/bin/env python3

from sys import argv

from bb_api import call


def get_clone_urls(key, limit, start):
    response = call('/rest/api/1.0/projects/{}/repos?limit={}&start={}'.format(key, limit, start))
    return response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1)


def get_all_clone_urls(keys):
    for key in keys:
        limit = 25
        start = 0
        is_last_page = False

        while not is_last_page:
            size, values, is_last_page, start = get_clone_urls(key, limit, start)

            if size:
                for value in values:
                    url = value['links']['clone'][0]['href']
                    yield key, value['slug'], url


if __name__ == '__main__':
    for project, repo, clone_url, in get_all_clone_urls(argv[1:]):
        clone_dir = '{}/{}'.format(project, repo.replace('.','/'))
        print('git clone {} {}'.format(clone_url, clone_dir))
