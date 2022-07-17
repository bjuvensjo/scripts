#!/usr/bin/env python3
import logging
from json import loads
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import post
from rich import print
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def create_json(repository_name: str) -> Dict:
    return {
        "triggers": [
            {
                "branchFilters": [],
                "pathFilters": [],
                "settingsSourceType": 2,
                "batchChanges": False,
                "maxConcurrentBuildsPerBranch": 1,
                "triggerType": "continuousIntegration",
            }
        ],
        "process": {"yamlFilename": "azure-pipelines.yml", "type": 2},
        "repository": {"name": repository_name, "type": "TfsGit"},
        "queue": {"id": 8},
        "name": repository_name,
    }


def do_create_build_definition(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    repository_name: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.7",
) -> Tuple[int, Dict]:
    url = f"{azure_devops_url}/{organization}/{project}/_apis/build/definitions?api-version={api_version}"
    params = {
        "json": create_json(repository_name),
        "url": url,
        "auth": ("", token),
        "verify": verify_certificate,
    }
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = post(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()
    return response.status_code, loads(response.text)


def parse_args(args):
    parser = get_parser("Create a build definition")
    parser.add_argument(
        "repository_name",
        help="The Azure DevOps build definition to create, should be the name of an existing repo",
    )
    return parser.parse_args(args)


def create_build_definition(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    repository_name: str,
    verify_certificate: bool,
) -> None:
    status_code, _ = do_create_build_definition(
        azure_devops_url,
        token,
        organisation,
        project,
        repository_name,
        verify_certificate,
    )
    print(status_code)


def main() -> None:  # pragma: no cover
    create_build_definition(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
