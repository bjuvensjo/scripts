#!/usr/bin/env python3
import argparse
from sys import argv
from typing import Union
from zipfile import ZipFile

from requests import get


def download(output_file: Union[str, bytes, int], url: str, username: str, password: str) -> None:
    with open(output_file, 'wb') as f:
        f.write(get(url, auth=(username, password)).content)


def extract_zip(zip_file):
    with ZipFile(zip_file, 'r') as z:
        z.extractall()


def main(output_file: Union[str, bytes, int], url: str, username: str, password: str, extract: bool) -> None:
    download(output_file, url, username, password)
    if extract:
        extract_zip(output_file)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Download file (requires: pipenv install requests)')
    parser.add_argument('output_file', help='output file, e.g. ./eggs.zip')
    parser.add_argument('url',
                        help='url to download, e.g. http://localhost:9000/job/CSL_xml.ws_1.0.x/3/execution/node/3/ws/target/surefire-reports/*zip*/surefire-reports.zip')
    parser.add_argument('-u', '--username', help='username for basic auth')
    parser.add_argument('-p', '--password', help='password for basic auth')
    parser.add_argument('-e', '--extract', help='if download zip, use this option to extract', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    main(**parse_args(argv[1:]).__dict__)
