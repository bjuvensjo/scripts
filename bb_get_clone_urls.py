#!/usr/bin/env python3

import sys
import bb_api


def get_clone_urls(key, limit, start):
    response = bb_api.call(f"projects/{key}/repos?limit={limit}&start={start}")
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


if __name__ == "__main__":
    for project, repo, clone_url, in get_all_clone_urls(sys.argv[1:]):
        clone_dir = f"{project}/{repo.replace('.','/')}"
        print(f"git clone {clone_url} {clone_dir}")
