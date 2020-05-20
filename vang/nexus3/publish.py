#!/usr/bin/env python3

from argparse import ArgumentParser
from glob import glob
from os import environ
from os.path import basename
from sys import argv

from vang.maven.pom import get_pom_info
from vang.nexus3.upload import upload
from vang.nexus3.utils import get_artifact_base_uri, get_pom_path


def get_pom_publish_name(pom_path, artifact_id, version):
    pom_name = pom_path.split('/')[-1]
    return pom_name if pom_name.split(
        '.')[-1] == 'pom' else f'{artifact_id}-{version}.pom'


def get_publish_data(artifact_base_uri, path, name):
    return {
        'file_path': path,
        'repository_path': f'{artifact_base_uri}/{name}'
    }


def publish_maven_artifact(repository, pom_dirs, url, username, password):
    for pom_dir in pom_dirs:
        pom_info = get_pom_info(get_pom_path(pom_dir))
        base_uri = get_artifact_base_uri(pom_info['group_id'],
                                         pom_info['artifact_id'],
                                         pom_info['version'])

        publish_data = [get_publish_data(base_uri, pom_info['pom_path'],
                                         get_pom_publish_name(pom_info['pom_path'],
                                                              pom_info['artifact_id'],
                                                              pom_info['version']))] + \
                       [get_publish_data(base_uri, path, basename(path))
                        for path in
                        glob(f'{pom_dir}/**/*.jar', recursive=True) +
                        glob(f'{pom_dir}/**/*.war', recursive=True)]

        yield [
            upload(pd['file_path'], repository, pd['repository_path'], url, username, password)
            for pd in publish_data
        ]


def main(repository, dirs, url, username, password):
    for response in publish_maven_artifact(repository, dirs, url, username, password):
        print(response)


def parse_args(args):
    parser = ArgumentParser(description='Publish maven artifact to Nexus3')
    parser.add_argument(
        'repository', help='Nexus3 repository, e.g. z-release')
    parser.add_argument(
        '-d',
        '--dirs',
        nargs='*',
        default=['.'],
        help='Maven pom directories to extract artifact information from')
    parser.add_argument('-l', '--url', default=environ.get('NEXUS3_REST_URL', None),
                        help='Nexus3 url, e.g. http://nexus_host:8080')
    parser.add_argument('-u', '--username', default=environ.get('NEXUS3_USERNAME', None), help='Nexus3 username')
    parser.add_argument('-p', '--password', default=environ.get('NEXUS3_PASSWORD', None), help='Nexus3 password')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
