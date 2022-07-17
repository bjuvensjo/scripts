#!/usr/bin/env python3
import logging
from json import loads
from os.path import basename
from sys import argv
from typing import Dict

from requests import get
from rich import print
from vang.azdo.util import get_parser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))


def do_list_repos(
    azure_devops_url: str,
    token: str,
    organization: str,
    project: str,
    verify_certificate: bool = True,
    include_links: bool = False,
    include_all_urls: bool = False,
    include_hidden: bool = False,
    api_version: str = "6.1-preview.1",
) -> Dict:
    url = f"{azure_devops_url}/{organization}/{project}/_apis/git/repositories?includeLinks={include_links}&includeAllUrls={include_all_urls}&includeHidden={include_hidden}&api-version={api_version}"
    params = {"url": url, "auth": ("", token), "verify": verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f"response.status_code: {response.status_code}")
    logger.info(f"response.text: {response.text}")
    response.raise_for_status()
    return loads(response.text)


def parse_args(args):
    parser = get_parser("List repos")
    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        "-n", "--names", action="store_true", help="Get only repo names"
    )
    optional_group.add_argument(
        "-r",
        "--repo_specs",
        help="Print only organisation/project/name",
        action="store_true",
    )
    optional_group.add_argument(
        "-u", "--urls", action="store_true", help="Get only repo urls"
    )

    return parser.parse_args(args)


def list_repos(
    azure_devops_url: str,
    token: str,
    organisation: str,
    project: str,
    names: bool,
    repo_specs: bool,
    urls: bool,
    verify_certificate: bool,
) -> None:
    repos = do_list_repos(azure_devops_url, token, organisation, project, verify_certificate)
    if not any((names, repo_specs, urls)):
        print(repos)
    else:
        for r in repos["value"]:
            if names:
                print(r["name"])
            elif repo_specs:
                print(f'{organisation}/{project}/{r["name"]}')
            elif urls:
                print(r["remoteUrl"])


def main() -> None:  # pragma: no cover
    list_repos(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
