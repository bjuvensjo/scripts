#!/usr/bin/env python3
import logging
from json import loads
from os import name as os_name
from os import system
from os.path import basename
from sys import argv
from typing import Dict, Tuple

from requests import post
from rich import print
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def do_create_repo(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    repo: str,
    verify_certificate: bool = True,
    api_version: str = "6.1-preview.1",
) -> Tuple[int, Dict]:
    url = f"{azure_devops_url}/{organization}/{project}/_apis/git/repositories?api-version={api_version}"
    params = {
        "json": {"name": repo},
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
    parser = get_parser("Create a repo")
    parser.add_argument("repo", help="The Azure DevOps repo to create")
    return parser.parse_args(args)


def create_repo(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    repo: str,
    verify_certificate: bool,
) -> None:
    status_code, repo = do_create_repo(
        azure_devops_url, token, organisation, project, repo, verify_certificate
    )
    print(status_code)

    commands = (
        f'    git remote add origin {repo["remoteUrl"]}\n'
        "    git push -u origin --all"
    )
    print(
        "If you already have code ready to be pushed to this repository "
        "then run this in your terminal."
    )
    print(commands)
    if os_name == "posix":
        system(f'echo "{commands}\\c" | pbcopy')
        print("(The commands are copied to the clipboard)")


def main() -> None:  # pragma: no cover
    create_repo(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
