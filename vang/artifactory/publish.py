#!/usr/bin/env python3
import hashlib
import json
from argparse import ArgumentParser
from glob import glob
from sys import argv

from vang.artifactory import api
from vang.artifactory.utils import get_artifact_base_uri, get_pom_path
from vang.maven.pom import get_pom_info


def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()


def get_checksums(bytes):
    return hashlib.md5(bytes).hexdigest(), hashlib.sha1(
        bytes).hexdigest(), hashlib.sha256(bytes).hexdigest()


def get_checksum_headers(md5, sha1, sha256):
    return {
        'X-Checksum-Md5': md5,
        'X-Checksum-Sha1': sha1,
        # sha256 Not yet supported...
        'X-Checksum-Sha256': sha256
    }


def get_pom_publish_name(pom_path, artifact_id, version):
    pom_name = pom_path.split('/')[-1]
    return pom_name if pom_name.split('.')[-1] == 'pom' else '{}-{}.pom'.format(
        artifact_id, version)


def get_publish_data(artifact_base_uri, path, name):
    content = read_file(path)
    md5, sha1, sha256 = get_checksums(content)
    return {
        'content': content,
        'checksum_headers': get_checksum_headers(md5, sha1, sha256),
        'uri': '{}/{}'.format(artifact_base_uri, name)
    }


def publish_maven_artifact(repository, pom_dirs):
    for pom_dir in pom_dirs:
        pom_info = get_pom_info(get_pom_path(pom_dir))
        base_uri = get_artifact_base_uri(
            repository, pom_info['group_id'],
            pom_info['artifact_id'], pom_info['version'])

        publish_data = [get_publish_data(base_uri, pom_info['pom_path'],
                                         get_pom_publish_name(pom_info['pom_path'],
                                                              pom_info['artifact_id'],
                                                              pom_info['version']))] + \
                       [get_publish_data(base_uri, path, path.split('/')[-1]) for path in
                        glob('{}/**/*.jar'.format(pom_dir), recursive=True) +
                        glob('{}/**/*.war'.format(pom_dir), recursive=True)]

        yield [
            api.call(pd['uri'], pd['checksum_headers'], pd['content'], 'PUT')
            for pd in publish_data
        ]


def main(repository, dirs):
    for response in publish_maven_artifact(repository, dirs):
        print(json.dumps(json.loads(str(response).replace("'", '"')), indent=2))


def parse_args(args):
    parser = ArgumentParser(description='Publish maven artifact to Artifactory')
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
    args = parse_args(argv[1:])
    main(args.repository, args.dirs)
