#!/usr/bin/env python3
from argparse import ArgumentParser
from pprint import pprint
from re import fullmatch
from sys import argv

from requests import get

from vang.core.core import pmap_ordered


def get_repo_content(repo_key, url, username, password):
    response = get(f'{url}/api/storage/{repo_key}?list&deep=1&listFolders=1', auth=(username, password))
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def filter_repo_files(repo_files, excludes):
    return [f for f in repo_files if not (f['folder'] or any(fullmatch(e, f['uri']) for e in excludes))]


def create_key(artifact_spec):
    return artifact_spec['uri'] if artifact_spec['folder'] else f'{artifact_spec["uri"]}#{artifact_spec["sha1"]}'


def map_to_map(repo_files):
    return {create_key(s): s for s in repo_files}


def diff(a_repo_files, b_repo_files, excludes=('.*maven-metadata.xml',), only_keys=True):
    a_repo_files_map, b_repo_files_map = list(pmap_ordered(
        lambda repo_files: map_to_map(
            filter_repo_files(
                repo_files,
                excludes
            )
        ),
        (a_repo_files, b_repo_files),
        processes=2
    ))

    a_key_set = set(a_repo_files_map.keys())
    b_key_set = set(b_repo_files_map.keys())
    a_only_keys = a_key_set.difference(b_key_set)
    b_only_keys = b_key_set.difference(a_key_set)

    if only_keys:
        return a_only_keys, b_only_keys
    else:
        return (v for k, v in a_repo_files_map.items()
                if k in a_only_keys), (v for k, v in b_repo_files_map.items()
                                       if k in b_only_keys)


def diff_repos(repo_specs, excludes=('.*maven-metadata.xml',), only_keys=True):
    a_repo_content, b_repo_content = list(pmap_ordered(
        lambda spec: get_repo_content(**spec),
        repo_specs,
        processes=2
    ))
    return diff(a_repo_content['files'], b_repo_content['files'], excludes, only_keys)


def main(
        a_repo_key,
        a_artifactory_url,
        a_artifactory_username,
        a_artifactory_password,
        b_repo_key,
        b_artifactory_url,
        b_artifactory_username,
        b_artifactory_password,
):
    specs = (
        {
            'repo_key': a_repo_key,
            'artifactory_url': a_artifactory_url,
            'username': a_artifactory_username,
            'password': a_artifactory_password,
        },
        {
            'repo_key': b_repo_key,
            'artifactory_url': b_artifactory_url,
            'username': b_artifactory_username,
            'password': b_artifactory_password,
        },
    )
    a_only_keys, b_only_keys = diff_repos(specs)

    if a_only_keys:
        print('### Only in a ###')
        pprint(a_only_keys)
    if b_only_keys:
        print('### Only in b ###')
        pprint(b_only_keys)
    print('Done!')


def parse_args(args):
    parser = ArgumentParser(description='Diff content of repositories')
    parser.add_argument('a_repo_key', help='a repo key')
    parser.add_argument('a_artifactory_url', help='a artifactory url')
    parser.add_argument('a_artifactory_username', help='a artifactory username')
    parser.add_argument('a_artifactory_password', help='a artifactory password')
    parser.add_argument('b_repo_key', help='b repo key')
    parser.add_argument('b_artifactory_url', help='b artifactory url')
    parser.add_argument('b_artifactory_username', help='b artifactory username')
    parser.add_argument('b_artifactory_password', help='b artifactory password')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
