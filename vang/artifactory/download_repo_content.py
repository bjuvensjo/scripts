#!/usr/bin/env python3
from argparse import ArgumentParser
from os import makedirs
from sys import argv

from requests import get

from vang.artifactory.list_repo_content import get_repo_content
from vang.core.core import pmap_unordered


def download(output_file, url, username, password):
    with open(output_file, 'wb') as f:
        f.write(get(url, auth=(username, password)).content)
    return url, output_file


def get_path(base_dir, file):
    return f'{base_dir}{file}'


def get_url(artifactory_url, file):
    return f'{artifactory_url}{file}'


def create_dirs(base_dir, files):
    for f in files:
        if f['folder']:
            p = get_path(base_dir, f['uri'])
            makedirs(p, exist_ok=True)


def download_files(artifactory_url, base_dir, files, max_processes=10):
    files_and_urls = [(get_path(base_dir, f['uri']), get_url(artifactory_url, f['uri'])) for f in files if
                      not f['folder']]
    yield from pmap_unordered(lambda uaf: download(uaf[0], uaf[1], '', ''),
                              files_and_urls,
                              processes=max_processes)


def get_artifactory_url(repo_content):
    return repo_content['uri'].replace('api/storage/', '')


def download_repo_content(output_dir, repo_key):
    base_dir = f'{output_dir}/{repo_key}'
    repo_content = get_repo_content(repo_key)
    create_dirs(base_dir, repo_content['files'])
    artifactory_url = get_artifactory_url(repo_content)
    yield from download_files(artifactory_url, base_dir, repo_content['files'])


def main(output_dir, repo_key):
    for url, output_file in download_repo_content(output_dir, repo_key):
        print(url, '->', output_file)


def parse_args(args):
    parser = ArgumentParser(
        description='Download repository content')
    parser.add_argument(
        'output_dir',
        help='Output dir')
    parser.add_argument(
        'repo_key',
        help='Repository key, e.g. libs-release')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
