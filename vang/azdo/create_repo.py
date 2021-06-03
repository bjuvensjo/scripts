#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import name as os_name, system, environ
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import post

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def create_repo(token: str, organization: str, project: str, repo: str, verify_certificate: bool = True,
                api_version: str = '6.1-preview.1') -> Tuple[int, Dict]:
    url = f'{base_url}/{organization}/{project}/_apis/git/repositories?api-version={api_version}'
    params = {
        'json': {'name': repo},
        'url': url,
        'auth': ('', token),
        'verify': verify_certificate
    }
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = post(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()
    return response.status_code, loads(response.text)


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Create a repo')
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
        'repo',
        help='The Azure DevOps repo to create')
    parser.add_argument(
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, repo: str, azure_devops_url: str) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    status_code, repo = create_repo(token, organisation, project, repo)
    print(status_code)

    commands = f'    git remote add origin {repo["remoteUrl"]}\n' \
               '    git push -u origin 1.0.x'
    print('If you already have code ready to be pushed to this repository '
          'then run this in your terminal.')
    print(commands)
    if os_name == 'posix':
        system(f'echo "{commands}\c" | pbcopy')
        print('(The commands are copied to the clipboard)')


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
