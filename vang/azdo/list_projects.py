#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from sys import argv
from typing import Iterable

from requests import get

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def list_projects(token: str, organisation: str, names: bool,
                  project_specs: bool, verify_certificate: bool = True,
                  api_version: str = '6.1-preview.4') -> Iterable:
    url = f'{base_url}/{organisation}/_apis/projects?api-version={api_version}'
    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()

    projects = loads(response.text)
    if not any((names, project_specs)):
        return projects['value']
    return [r['name'] if names else f'{organisation}/{r["name"]}' for r in projects['value']]


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='List projects')
    parser.add_argument(
        '--token',
        default=environ.get('AZDO_TOKEN', ''),
        help='The Azure DevOps authorisation token')
    parser.add_argument(
        '--organisation',
        default=environ.get('AZDO_ORGANISATION', ''),
        help='The Azure DevOps organisation')
    parser.add_argument(
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        '-n', '--names', action='store_true', help='Get only project names')
    optional_group.add_argument(
        '-r',
        '--project_specs',
        help='Print only organisation/project',
        action='store_true')

    return parser.parse_args(args)


def main(token: str, organisation: str, azure_devops_url: str, names: bool,
         project_specs: bool) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    for p in list_projects(token, organisation, names, project_specs):
        print(p)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
