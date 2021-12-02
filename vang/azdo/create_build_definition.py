#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import post

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def create_json(repository_name: str) -> Dict:
    return {
        "triggers": [
            {
                "branchFilters": [],
                "pathFilters": [],
                "settingsSourceType": 2,
                "batchChanges": False,
                "maxConcurrentBuildsPerBranch": 1,
                "triggerType": "continuousIntegration"
            }
        ],
        "process": {
            "yamlFilename": "azure-pipelines.yml",
            "type": 2
        },
        "repository": {
            "name": repository_name,
            "type": "TfsGit"
        },
        "queue": {
            "id": 8
        },
        "name": repository_name
    }


def create_build_definition(token: str, organization: str, project: str, repository_name: str,
                            verify_certificate: bool = True,
                            api_version: str = '6.1-preview.7') -> Tuple[int, Dict]:
    url = f'{base_url}/{organization}/{project}/_apis/build/definitions?api-version={api_version}'
    params = {
        'json': create_json(repository_name),
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
        description='Create a build_definition')
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
        'repository_name',
        help='The Azure DevOps build definition to create, should be the name of an existing repo')
    parser.add_argument(
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, repository_name: str,
         azure_devops_url: str) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    status_code, build_definition = create_build_definition(token, organisation, project, repository_name)
    print(status_code)
    # pprint(build_definition)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
