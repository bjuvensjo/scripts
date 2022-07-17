#!/usr/bin/env python3
import logging
from json import loads
from os.path import basename
from sys import argv
from typing import Iterable

from requests import get
from rich import print
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def do_list_projects(
    azure_devops_url: str,
    token: str,
    organisation: str,
    names: bool,
    project_specs: bool,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.4",
) -> dict | Iterable:
    url = f"{azure_devops_url}/{organisation}/_apis/projects?api-version={api_version}"
    params = {"url": url, "auth": ("", token), "verify": verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()

    projects = loads(response.text)
    if not any((names, project_specs)):
        return projects
    return [
        p["name"] if names else f'{organisation}/{p["name"]}' for p in projects["value"]
    ]


def parse_args(args):
    parser = get_parser("List projects", False)
    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        "-n", "--names", action="store_true", help="Get only project names"
    )
    optional_group.add_argument(
        "-r",
        "--project_specs",
        help="Print only organisation/project",
        action="store_true",
    )

    return parser.parse_args(args)


def list_projects(
    azure_devops_url: str,
    token: str,
    organisation: str,
    names: bool,
    project_specs: bool,
    verify_certificate: bool,
) -> None:
    projects = do_list_projects(
        azure_devops_url, token, organisation, names, project_specs, verify_certificate
    )
    if isinstance(projects, dict):
        print(projects)
    else:
        for p in projects:
            print(p)


def main() -> None:  # pragma: no cover
    list_projects(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
