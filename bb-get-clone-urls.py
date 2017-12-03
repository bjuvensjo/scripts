#!/usr/bin/env python3

from json import loads
from os import environ
from base64 import encodebytes
import sys
import urllib.request


def get_basic_auth_header(username, password):
    auth = f"{username}:{password}"
    return f"Basic {encodebytes(auth.encode()).decode('UTF-8').strip()}"


def get_clone_urls(key, limit, start):
    request = urllib.request.Request(f"http://cuso.edb.se/stash/rest/api/1.0/projects/{key}/repos?limit={limit}&start={start}")
    request.add_header("Authorization", get_basic_auth_header(environ['U'], environ['P']))

    data = urllib.request.urlopen(request).read()
    response =  loads(data.decode('UTF-8'))
    return (response['size'], response['values'], response['isLastPage'], response.get('nextPageStart', -1))


def get_all_clone_urls(keys):
    for key in keys:
        limit = 25
        start = 0
        is_last_page = False

        while not is_last_page:
            size, values, is_last_page, start = get_clone_urls(key, limit, start)

            if size:
                for value in values:
                    clone_url = value['links']['clone'][0]['href']
                    clone_dir = f"{key}/{value['slug'].replace('.','/')}"
                    print(f"git clone {clone_url} {clone_dir}")                    


if __name__ == "__main__":
    get_all_clone_urls(sys.argv[1:])
