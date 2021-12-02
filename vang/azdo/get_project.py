#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from pprint import pprint
from sys import argv
from typing import Dict

from requests import get

from vang.azdo.list_projects import list_projects

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def get_project_id(token: str, organization: str, project: str, verify_certificate: bool,
                   api_version: str = '6.1-preview.4') -> str:
    for p in list_projects(token, organization, verify_certificate, api_version)['value']:
        if p['name'] == project:
            return p['id']
    return 'project_not_found'


def get_project(token: str, organization: str, project: str, verify_certificate: bool = True,
                api_version: str = '6.1-preview.4') -> Dict:
    project_id = get_project_id(token, organization, project, verify_certificate, api_version)
    url = f'{base_url}/{organization}/_apis/projects/{project_id}?api-version={api_version}'
    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()
    return loads(response.text)


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Get project')
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

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        '-i', '--project_id', action='store_true', help='Get only project id')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, azure_devops_url: str,
         project_id: bool) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    project = get_project(token, organisation, project)
    if not project_id:
        pprint(project)
    else:
        print(project['id'])


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
