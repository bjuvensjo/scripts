#!/usr/bin/env python3
from argparse import ArgumentParser
from os import environ
from sys import argv

from requests import put


def read_file(file_path):  # pragma: no cover
    with open(file_path, 'rb') as f:
        return f.read()


def upload(file_path, repository, repository_path, url, username, password):
    url = f'{url}/repository/{repository}/{repository_path}'
    data = read_file(file_path)
    headers = {'Content-Type': 'application/octet-stream'}
    response = put(url, data=data, headers=headers, auth=(username, password))
    if response.status_code != 201:
        raise OSError(f'{response.status_code}, {response.content}')
    return response.status_code


def parse_args(args):
    parser = ArgumentParser(description='Get assets')
    parser.add_argument('file_path', help='File to upload, e.g. ./myartifact-1.0.0.jar')
    parser.add_argument('repository', help='Nexus3 repository, e.g. maven-releases')
    parser.add_argument('repository_path',
                        help='Path within Nexus3 repository, e.g com/myorg/myartifact/1.0.0/myartifact-1.0.0.jar')
    parser.add_argument('-l', '--url', default=environ.get('NEXUS3_REST_URL', None),
                        help='Nexus3 url, e.g. http://nexus_host:8080')
    parser.add_argument('-u', '--username', default=environ.get('NEXUS3_USERNAME', None), help='Nexus3 username')
    parser.add_argument('-p', '--password', default=environ.get('NEXUS3_PASSWORD', None), help='Nexus3 password')
    return parser.parse_args(args)


def main(file_path, repository, repository_path, url, username, password):
    print(upload(file_path, repository, repository_path, url, username, password))


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
