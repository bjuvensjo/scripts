#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.artifactory import utils
from vang.artifactory import api
from vang.maven.pom import get_pom_info


def delete_maven_artifact(repository, pom_dirs):
    for pom_dir in pom_dirs:
        pom_info = get_pom_info(utils.get_pom_path(pom_dir))
        base_uri = utils.get_artifact_base_uri(
            repository,
            pom_info['group_id'],
            pom_info['artifact_id'],
            pom_info['version'],
        )
        yield api.call(base_uri, method='DELETE')


def main(repository, pom_dirs):
    for response in delete_maven_artifact(repository, pom_dirs):
        print(response)


def parse_args(args):
    parser = ArgumentParser(
        description='Delete maven artifact from Artifactory')
    parser.add_argument(
        'repository', help='Artifactory repository, e.g. z-release')
    parser.add_argument(
        '-d',
        '--dirs',
        nargs='*',
        default=['.'],
        help='Maven pom directories to extract artifact information from')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv)
    main(args.repository, args.dirs)
