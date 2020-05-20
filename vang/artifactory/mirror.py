#!/usr/bin/env python3
import hashlib
from itertools import count
from json import dumps
from os import makedirs
from os.path import exists

from requests import get, put

import vang.artifactory.mirror_config as config
from vang.artifactory.diff_repos import diff, get_repo_content
from vang.core.core import pmap_unordered
from vang.misc.version import get_latest_snapshot, get_latest_rc, get_latest_fixed


def read_file(file_path):  # pragma: no cover
    with open(file_path, 'rb') as f:
        return f.read()


def get_checksums(the_bytes):
    return (
        hashlib.md5(the_bytes).hexdigest(),
        hashlib.sha1(the_bytes).hexdigest(),
        hashlib.sha256(the_bytes).hexdigest()
    )


def sha1sum(file_path):
    return get_checksums(read_file(file_path))[1]


def download_file(output_file, url, sha1, retry=True):
    if exists(output_file) and sha1sum(output_file) == sha1:
        return True, 'Already downloaded'
    with open(output_file, 'wb') as f:
        result = get(url)
        if result.status_code == 200:
            f.write(result.content)
            if sha1sum(output_file) == sha1:
                return True, 'Downloaded and verified sha1'
            else:
                if retry:
                    return download_file(output_file, url, sha1, False)
                else:
                    return False, 'Downloaded with bad sha1'
        else:
            if retry:
                return download_file(output_file, url, sha1, False)
            else:
                return False, f'{result.status_code}: {result.content}'


def get_checksum_headers(md5, sha1, sha256):
    return {
        'X-Checksum-Md5': md5,
        'X-Checksum-Sha1': sha1,
        'X-Checksum-Sha256': sha256
    }


def mirror_file(repo_work_dir, from_repo_uri, artifact_spec, to_repo_uri, to_repo_username,
                to_repo_password):
    state = {
        'download_url': f'{from_repo_uri}{artifact_spec["uri"]}',
    }
    # download
    d, f = artifact_spec['uri'].rsplit('/', maxsplit=1)
    output_dir = f'{repo_work_dir}{d}'
    makedirs(output_dir, exist_ok=True)
    state['download_output_file'] = f'{repo_work_dir}{artifact_spec["uri"]}'
    download_result, download_message = download_file(state['download_output_file'], state['download_url'],
                                                      artifact_spec['sha1'],
                                                      True)
    # TODO Return checksums from download and use in upload
    state['download_result'] = download_result
    state['download_message'] = download_message

    # upload
    if download_result:
        content = read_file(state['download_output_file'])
        md5, sha1, sha256 = get_checksums(content)
        state['headers'] = {
            **get_checksum_headers(md5, sha1, sha256),
            'Content-Type': 'application/octet-stream'
        }
        state['upload_url'] = f'{to_repo_uri}{artifact_spec["uri"]}'
        upload_result = put(state['upload_url'], data=content, headers=state['headers'],
                            auth=(to_repo_username, to_repo_password))
        state['upload_result'] = upload_result.status_code == 201
        state['upload_status_code'] = upload_result.status_code
        state['upload_response'] = upload_result.text
        state['result'] = state['upload_result']

    return state


def not_folders(repo_files):
    return filter(lambda r: not r['folder'], repo_files)


def not_maven_metadata(repo_files):
    return filter(lambda r: not r['uri'].endswith('maven-metadata.xml'), repo_files)


def not_index(repo_files):
    return filter(lambda r: '.index' not in r['uri'], repo_files)


def latest_version(repo_files):
    version_map = {}
    for repo_file in repo_files:
        uri = repo_file['uri']
        group_and_artifact_id = '/'.join(uri.split('/')[:-2])
        version = uri.split('/')[-2]
        if group_and_artifact_id not in version_map:
            version_map[group_and_artifact_id] = []
        version_map[group_and_artifact_id].append(version)

    latest_version_map = {}
    for k, v in version_map.items():
        try:
            latest_version_map[k] = [get_latest_snapshot(v), get_latest_rc(v), get_latest_fixed(v)]
        except ValueError:
            latest_version_map[k] = v

    latest_repo_files = []
    for repo_file in repo_files:
        uri = repo_file['uri']
        group_and_artifact_id = '/'.join(uri.split('/')[:-2])
        version = uri.split('/')[-2]
        if version in latest_version_map[group_and_artifact_id]:
            latest_repo_files.append(repo_file)

    return latest_repo_files


def filter_repo_files(repo_files, filters):
    print(f'all: {len(repo_files)}')
    for f in filters:
        repo_files = f(repo_files)
        repo_files = list(repo_files)
        print(f'{f.__name__}: {len(repo_files)}')
    return repo_files


# TODO Maybe use "Last downloaded" to filter out even more
# Note that files ending SNAPSHOT.* in from repo will get SNAPSHOT replaced
# by a timestamp in to repo and thus will not be found in to_uri
# on a rerun of this script. For now, nothing will be done about that.
def mirror(filters, max_processes=10):
    for repo_key in config.repositories:
        if type(repo_key) is str:
            from_repo_key = repo_key
            to_repo_key = repo_key
        else:
            from_repo_key, to_repo_key = repo_key

        from_repo_files = get_repo_content(from_repo_key, **config.from_artifactory_spec)['files']
        filtered_from_repo_files = filter_repo_files(from_repo_files, filters)

        to_repo_files = get_repo_content(to_repo_key, **config.to_artifactory_spec)['files']
        files_not_in_to_repo, files_not_in_from_repo = diff(filtered_from_repo_files, to_repo_files, only_keys=False)
        files_not_in_to_repo = list(files_not_in_to_repo)
        print('Not in to repo:', len(files_not_in_to_repo))

        from_repo_uri = f'{config.from_artifactory_spec["url"]}/{from_repo_key}'
        to_repo_uri = f'{config.to_artifactory_spec["url"]}/{to_repo_key}'
        yield from pmap_unordered(
            lambda artifact_spec: mirror_file(f'{config.work_dir}/{from_repo_key}', from_repo_uri, artifact_spec,
                                              to_repo_uri, config.to_artifactory_spec['username'],
                                              config.to_artifactory_spec['password']),
            files_not_in_to_repo,
            processes=max_processes)


if __name__ == '__main__':
    verbose = True
    for n, m in zip(count(), mirror(config.filters)):
        if verbose or not m['result']:
            print(n, dumps(m))
    print('Done!')
