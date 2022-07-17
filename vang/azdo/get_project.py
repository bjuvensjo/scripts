#!/usr/bin/env python3
import logging
from json import loads
from os.path import basename
from sys import argv
from typing import Dict

from requests import get
from rich import print
from vang.azdo.list_projects import do_list_projects
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def get_project_id(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    verify_certificate: bool,
    api_version: str = "6.1-preview.4",
) -> str:
    for p in do_list_projects(
        azure_devops_url,
        token,
        organization,
        False,
        False,
        verify_certificate,
        api_version,
    )["value"]:
        if p["name"] == project:
            return p["id"]
    return "project_not_found"


def do_get_project(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.4",
) -> Dict:
    project_id = get_project_id(
        azure_devops_url, token, organization, project, verify_certificate, api_version
    )
    url = f"{azure_devops_url}/{organization}/_apis/projects/{project_id}?api-version={api_version}"
    params = {"url": url, "auth": ("", token), "verify": verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()
    return loads(response.text)


def parse_args(args):
    parser = get_parser("Get project")
    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        "-i", "--project_id", action="store_true", help="Get only project id"
    )

    return parser.parse_args(args)


def get_project(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    project_id: bool,
    verify_certificate: bool,
) -> None:
    project = do_get_project(
        azure_devops_url, token, organisation, project, verify_certificate
    )
    if project_id:
        print(project["id"])
    else:
        print(project)


def main() -> None:  # pragma: no cover
    get_project(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
