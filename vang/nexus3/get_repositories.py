#!/usr/bin/env python3

from argparse import ArgumentParser
from os import environ
from pprint import pprint
from sys import argv

from requests import get


def get_repositories(url, username, password):
    url = f'{url}/service/rest/v1/repositories'
    response = get(url, auth=(username, password))
    if response.status_code != 200:
        raise OSError(f'{response.status_code}, {response.content}')
    return response.json()


def parse_args(args):
    parser = ArgumentParser(description='Get repositories')
    parser.add_argument('-l', '--url', default=environ.get('NEXUS3_REST_URL', None),
                        help='Nexus3 url, e.g. http://nexus_host:8080')
    parser.add_argument('-u', '--username', default=environ.get('NEXUS3_USERNAME', None), help='Nexus3 username')
    parser.add_argument('-p', '--password', default=environ.get('NEXUS3_PASSWORD', None), help='Nexus3 password')
    return parser.parse_args(args)


def main(url, username, password):
    pprint(get_repositories(url, username, password))


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
