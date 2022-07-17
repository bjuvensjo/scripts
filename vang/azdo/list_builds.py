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


def do_list_builds(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.6",
) -> Iterable:
    url = f"{azure_devops_url}/{organisation}/{project}/_apis/build/builds?api-version={api_version}"
    params = {"url": url, "auth": ("", token), "verify": verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()

    builds = loads(response.text)
    return builds


def parse_args(args):
    parser = get_parser("List builds")
    return parser.parse_args(args)


def list_builds(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    verify_certificate: bool,
) -> None:
    builds = do_list_builds(
        azure_devops_url, token, organisation, project, verify_certificate
    )
    print(builds)


def main() -> None:  # pragma: no cover
    list_builds(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
