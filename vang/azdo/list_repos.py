#!/usr/bin/env python3
import argparse
import logging
from json import loads
from os import environ
from os.path import basename
from pprint import pprint
from sys import argv
from typing import Dict

from requests import get

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(basename(__file__))

base_url = 'https://dev.azure.com'


def list_repos(token: str, organization: str, project: str, verify_certificate: bool = True,
               include_links: bool = False, include_all_urls: bool = False, include_hidden: bool = False,
               api_version: str = '6.1-preview.1') -> Dict:
    url = f'{base_url}/{organization}/{project}/_apis/git/repositories?includeLinks={include_links}&includeAllUrls={include_all_urls}&includeHidden={include_hidden}&api-version={api_version}'
    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    logger.info(f'params: {str(params).replace(token, "***")}')
    response = get(**params)
    logger.info(f'response.status_code: {response.status_code}')
    logger.info(f'response.text: {response.text}')
    response.raise_for_status()
    return loads(response.text)


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='List repos')
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
        '-au',
        '--azure_devops_url',
        default='https://dev.azure.com',
        help='The Azure DevOps REST API base url')

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        '-n', '--names', action='store_true', help='Get only repo names')
    optional_group.add_argument(
        '-r',
        '--repo_specs',
        help='Print only organisation/project/name',
        action='store_true')
    optional_group.add_argument(
        '-u', '--urls', action='store_true', help='Get only repo urls')

    return parser.parse_args(args)


def main(token: str, organisation: str, project: str, azure_devops_url: str, names: bool, repo_specs: bool,
         urls: bool) -> None:  # pragma: no cover
    global base_url
    base_url = azure_devops_url

    repos = list_repos(token, organisation, project)
    if not any((names, repo_specs, urls)):
        pprint(repos)
    else:
        for r in repos['value']:
            if names:
                print(r['name'])
            elif repo_specs:
                print(f'{organisation}/{project}/{r["name"]}')
            elif urls:
                print(r['remoteUrl'])


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
