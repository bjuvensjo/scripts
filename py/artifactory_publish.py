#!/usr/bin/env python3
import hashlib
import json
from glob import glob
from os.path import exists, basename

from sys import argv

import artifactory_api as api
import maven_pom


def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()


def get_checksums(bytes):
    return hashlib.md5(bytes).hexdigest(), hashlib.sha1(bytes).hexdigest(), hashlib.sha256(bytes).hexdigest()


def get_checksum_headers(md5, sha1, sha256):
    return {
        'X-Checksum-Md5': md5,
        'X-Checksum-Sha1': sha1,
        'X-Checksum-Sha256': sha256  # Not yet supported, see https://www.jfrog.com/jira/browse/RTFACT-6962
    }


def get_pom_path(work_dir):
    pom_path = '{}/pom.xml'.format(work_dir)
    if exists(pom_path):
        return pom_path

    pom_paths = glob("{}/*.pom".format(work_dir), recursive=True)
    if not pom_paths:
        raise ValueError('No pom in {}'.format(work_dir))
    if len(pom_paths) == 1:
        return pom_paths[0]
    return sorted(pom_paths, key=len)[0]  # The pom without timestamp


def get_artifact_base_uri(artifactory_repository, group_id, artifact_id, version):
    return '/{}/{}/{}/{}'.format(artifactory_repository,
                                 '/'.join(group_id.split('.')),
                                 artifact_id,
                                 version)


def get_pom_publish_name(pom_path, artifact_id, version):
    pom_name = pom_path.split('/')[-1]
    return pom_name if pom_name.split('.')[-1] == 'pom' else '{}-{}.pom'.format(artifact_id, version)


def get_publish_data(artifact_base_uri, path, name):
    content = read_file(path)
    md5, sha1, sha256 = get_checksums(content)
    return {
        'content': content,
        'checksum_headers': get_checksum_headers(md5, sha1, sha256),
        'uri': '{}/{}'.format(artifact_base_uri, name)
    }


def publish_maven_artifact(artifactory_repository, pom_dirs):
    for pom_dir in pom_dirs:
        pom_info = maven_pom.get_pom_info(get_pom_path(pom_dir))
        base_uri = get_artifact_base_uri(artifactory_repository,
                                         pom_info['group_id'],
                                         pom_info['artifact_id'],
                                         pom_info['version'])

        publish_data = [get_publish_data(base_uri, pom_info['pom_path'],
                                         get_pom_publish_name(pom_info['pom_path'], pom_info['artifact_id'],
                                                              pom_info['version']))] + \
                       [get_publish_data(base_uri, path, path.split('/')[-1]) for path in
                        glob('{}/**/*.jar'.format(pom_dir), recursive=True) +
                        glob('{}/**/*.war'.format(pom_dir), recursive=True)]

        yield [api.call(pd['uri'], pd['checksum_headers'], pd['content'], 'PUT') for pd in publish_data]


if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: {} artifactory_repository [pom_dirs]'.format(basename(__file__)))
    else:
        artifactory_repository = argv[1]
        pom_dirs = argv[2:] if len(argv) > 2 else ['.']
        responses = publish_maven_artifact(artifactory_repository, pom_dirs)
        for response in responses:
            print(json.dumps(json.loads(str(response).replace("'", '"')), indent=2))
