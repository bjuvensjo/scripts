#!/usr/bin/env python3
from glob import glob
from os.path import exists


def get_pom_path(pom_dir):
    pom_path = f'{pom_dir}/pom.xml'
    if exists(pom_path):
        return pom_path

    pom_paths = glob(f'{pom_dir}/*.pom', recursive=True)
    if not pom_paths:
        raise ValueError(f'No pom in {pom_dir}')
    if len(pom_paths) == 1:
        return pom_paths[0]
    return sorted(pom_paths, key=len)[0]  # The pom without timestamp


def get_artifact_base_uri(repository, group_id, artifact_id, version):
    return f'/{repository}/{"/".join(group_id.split("."))}/{artifact_id}/{version}'
