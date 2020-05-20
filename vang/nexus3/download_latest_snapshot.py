#!/usr/bin/env python3
from argparse import ArgumentParser
from os import environ
from sys import argv
from xml.etree.ElementTree import fromstring

from requests import get


def get_metadata(root_url, username, password):
    response = get(f'{root_url}/maven-metadata.xml', auth=(username, password))
    e = fromstring(response.text)
    p = 'versioning/snapshotVersions/snapshotVersion'
    return e.findtext(f'{p}/value').strip(), e.findtext(f'{p}/extension').strip()


def download(output_file, url, username, password):
    with open(output_file, 'wb') as f:
        f.write(get(url, auth=(username, password)).content)


def main(output_dir, nexus_url, repo, group_id, artifact_id, version,
         username=environ.get('NEXUS3_USERNAME', None),
         password=environ.get('NEXUS3_PASSWORD', None)):
    root_url = f'{nexus_url}/{repo}/{group_id.replace(".", "/")}/{artifact_id}/{version}'
    snapshot_version, extension = get_metadata(root_url, username, password)
    output_file = f'{output_dir}/{artifact_id}-{version}.{extension}'
    url = f'{root_url}/{artifact_id}-{snapshot_version}.{extension}'
    print(f'Downloading: {url} to {output_file}')
    download(
        output_file,
        url,
        username,
        password
    )
    print(f'Downloaded: {url} to {output_file}')


def parse_args(args):
    parser = ArgumentParser(description='Download is_later snapshot from Nexus (requires: pipenv install requests)')
    parser.add_argument('output_dir', help='output dir')
    parser.add_argument('nexus_url',
                        help='Nexus url, e.g. http://localhost:9002/repository')
    parser.add_argument('repo', help='Nexus repository, e.g. maven-snapshots')
    parser.add_argument('group_id', help='Maven group id')
    parser.add_argument('artifact_id', help='Maven artifact id')
    parser.add_argument('version', help='Maven version')
    parser.add_argument('-u', '--username', help='username for basic auth')
    parser.add_argument('-p', '--password', help='password for basic auth')
    return parser.parse_args(args)


if __name__ == '__main__':
    main(**parse_args(argv[1:]).__dict__)
