#!/usr/bin/env python3
import logging
from json import loads
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import get, post
from rich import print
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def get_definition_id(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    build_definition_name: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.7",
):
    url = f"{azure_devops_url}/{organization}/{project}/_apis/build/definitions?name={build_definition_name}&api-version={api_version}"
    params = {"url": url, "auth": ("", token), "verify": verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()
    return loads(response.text)["value"][0]["id"]


def create_json(definition_id: int, branch: str) -> Dict:
    return {"definition": {"id": definition_id}, "sourceBranch": f"refs/heads/{branch}"}


def do_queue_build(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    build_definition_name: str,
    branch: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.6",
) -> Tuple[int, Dict]:
    definition_id = get_definition_id(
        azure_devops_url,
        token,
        organization,
        project,
        build_definition_name,
        verify_certificate,
    )
    url = f"{azure_devops_url}/{organization}/{project}/_apis/build/builds?api-version={api_version}"
    params = {
        "json": create_json(definition_id, branch),
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
    parser = get_parser("Queue a build")
    parser.add_argument(
        "build_definition_name",
        help="The Azure DevOps build definition name to queue",
    )
    parser.add_argument(
        "branch",
        help="The Azure DevOps repo branch to build",
    )

    return parser.parse_args(args)


def queue_build(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    build_definition_name: str,
    branch: str,
    verify_certificate: bool,
) -> None:
    status_code, _ = do_queue_build(
        azure_devops_url,
        token,
        organisation,
        project,
        build_definition_name,
        branch,
        verify_certificate,
    )
    print(status_code)


def main() -> None:  # pragma: no cover
    queue_build(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
