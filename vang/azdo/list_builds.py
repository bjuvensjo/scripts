#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from pprint import pprint
from sys import argv
from typing import Iterable

from requests import get

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def list_builds(token: str, organisation: str, project: str, verify_certificate: bool = True,
                api_version: str = '6.1-preview.6') -> Iterable:
    url = f'{base_url}/{organisation}/{project}/_apis/build/builds?api-version={api_version}'
    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()

    builds = loads(response.text)
    return builds['value']


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='List builds')
    parser.add_argument(
        '--token',
        default=environ.get('AZDO_TOKEN', ''),
        help='The Azure DevOps authorisation token')
    parser.add_argument(
        '--organisation',
        default=environ.get('AZDO_ORGANISATION', ''),
        help='The Azure DevOps organisation')
    parser.add_argument(
        '--project',
        default=environ.get('AZDO_PROJECT', ''),
        help='The Azure DevOps project')
    parser.add_argument(
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, azure_devops_url: str) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    for p in list_builds(token, organisation, project):
        pprint(p)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
