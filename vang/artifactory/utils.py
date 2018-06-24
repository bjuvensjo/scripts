#!/usr/bin/env python3
from glob import glob
from os.path import exists


def get_pom_path(pom_dir):
    pom_path = '{}/pom.xml'.format(pom_dir)
    if exists(pom_path):
        return pom_path

    pom_paths = glob('{}/*.pom'.format(pom_dir), recursive=True)
    if not pom_paths:
        raise ValueError('No pom in {}'.format(pom_dir))
    if len(pom_paths) == 1:
        return pom_paths[0]
    return sorted(pom_paths, key=len)[0]  # The pom without timestamp


def get_artifact_base_uri(repository, group_id, artifact_id, version):
    return '/{}/{}/{}/{}'.format(repository,
                                 '/'.join(group_id.split('.')),
                                 artifact_id,
                                 version)
