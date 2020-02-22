#!/usr/bin/env python3
import hashlib
from itertools import count
from json import dumps
from os import remove, makedirs
from os.path import exists

from requests import get, put

import vang.artifactory.mirror_config as config
from vang.artifactory.diff_repos import diff_repos
from vang.core.core import pmap_unordered


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
    if not exists(output_file) or sha1sum(output_file) != sha1:
        with open(output_file, 'wb') as f:
            f.write(get(url).content)

    if sha1sum(output_file) == sha1:
        return True
    else:
        if retry:
            remove(output_file)
            return download_file(output_file, url, sha1, False)
        return False


def get_checksum_headers(md5, sha1, sha256):
    return {
        'X-Checksum-Md5': md5,
        'X-Checksum-Sha1': sha1,
        'X-Checksum-Sha256': sha256
    }


def mirror_file(repo_work_dir, from_repo_uri, artifact_spec, exclude_function, to_repo_uri, to_repo_username,
                to_repo_password):
    state = {
        'download_url': f'{from_repo_uri}{artifact_spec["uri"]}',
        'excluded': exclude_function(from_repo_uri, artifact_spec)
    }
    if state['excluded']:
        state['result'] = True
    else:
        # download
        d, f = artifact_spec['uri'].rsplit('/', maxsplit=1)
        output_dir = f'{repo_work_dir}{d}'
        makedirs(output_dir, exist_ok=True)
        state['download_output_file'] = f'{repo_work_dir}{artifact_spec["uri"]}'
        download_result = download_file(state['download_output_file'], state['download_url'], artifact_spec['sha1'],
                                        True)
        # TODO Return checksums from download and use in upload
        state['download_result'] = download_result

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


# TODO Maybe use "Last downloaded" to filter out even more
# Note that files ending SNAPSHOT.* in from repo will get SNAPSHOT replaced
# by a timestamp in to repo and thus will not be found in to_uri
# on a rerun of this script. For now, nothing will be done about that.
def mirror(max_processes=10):
    for repo_key in config.repositories:
        if type(repo_key) is str:
            from_repo_key = repo_key
            to_repo_key = repo_key
        else:
            from_repo_key, to_repo_key = repo_key

        files_not_in_to_repo, files_not_in_from_repo = diff_repos(
            (
                dict(config.from_artifactory_spec,
                     artifactory_url=config.from_artifactory_spec['url'],
                     repo_key=from_repo_key),
                dict(config.to_artifactory_spec,
                     artifactory_url=config.to_artifactory_spec['url'],
                     repo_key=to_repo_key),
            ),
            only_keys=False)

        from_repo_uri = f'{config.from_artifactory_spec["url"]}/{from_repo_key}'
        to_repo_uri = f'{config.to_artifactory_spec["url"]}/{to_repo_key}'
        yield from pmap_unordered(
            lambda artifact_spec: mirror_file(f'{config.work_dir}/{from_repo_key}', from_repo_uri, artifact_spec,
                                              config.is_excluded, to_repo_uri, config.to_artifactory_spec['username'],
                                              config.to_artifactory_spec['password']),
            files_not_in_to_repo,
            processes=max_processes)


if __name__ == '__main__':
    verbose = True
    for n, m in zip(count(), mirror()):
        if verbose or not m['result']:
            print(n, dumps(m))
    print('Done!')
