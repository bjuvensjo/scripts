#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import post, get

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def get_definition_id(token: str, organization: str, project: str, build_definition_name: str,
                      verify_certificate: bool = True,
                      api_version: str = '6.1-preview.7'):
    url = f'{base_url}/{organization}/{project}/_apis/build/definitions?name={build_definition_name}&api-version={api_version}'
    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()
    return loads(response.text)['value'][0]['id']


def create_json(definition_id: int, branch: str) -> Dict:
    return {
        "definition": {
            "id": definition_id
        },
        "sourceBranch": f"refs/heads/{branch}"
    }


def queue_build(token: str, organization: str, project: str, build_definition_name: str,
                branch: str,
                verify_certificate: bool = True,
                api_version: str = '6.1-preview.6') -> Tuple[int, Dict]:
    definition_id = get_definition_id(token, organization, project, build_definition_name, verify_certificate)
    url = f'{base_url}/{organization}/{project}/_apis/build/builds?api-version={api_version}'
    params = {
        'json': create_json(definition_id, branch),
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
        description='Queue a build')
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
        'build_definition_name',
        help='The Azure DevOps build definition name to queue')
    parser.add_argument(
        'branch',
        help='The Azure DevOps repo branch to build')
    parser.add_argument(
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, build_definition_name: str, branch: str,
         azure_devops_url: str) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    status_code, build = queue_build(token, organisation, project, build_definition_name, branch)
    print(status_code)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
