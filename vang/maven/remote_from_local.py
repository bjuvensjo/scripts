#!/usr/bin/env python3
from argparse import ArgumentParser
from os import environ, path, walk
from os.path import normpath, exists
from sys import argv
from xml.etree.ElementTree import parse

NAME_SPACES = {'ns': 'http://maven.apache.org/SETTINGS/1.0.0'}


def text(e, n):
    return e.findtext(f'ns:{n}', namespaces=NAME_SPACES)


def findall(e, n):
    return e.findall(f'.//ns:{n}', namespaces=NAME_SPACES)


def get_settings_info(settings_path):
    e = parse(normpath(settings_path))

    local_repo = text(e, 'localRepository')
    if '${user.home}' in local_repo:
        local_repo = local_repo.replace('${user.home}', environ['HOME'])

    remotes = {text(r, 'id'): text(r, 'url')
               for r in findall(e, 'repository')}

    plugin_remotes = {text(r, 'id'): text(r, 'url')
                      for r in findall(e, 'pluginRepository')}

    mirrors = {text(r, 'id'): text(r, 'url')
               for r in findall(e, 'mirror')}

    return local_repo, {**remotes, **plugin_remotes, **mirrors}


def excluded(f):
    if f in ['_remote.repositories',
             'maven-metadata-local.xml',
             'maven-metadata-ossrh.xml',
             'resolver-status.properties']:
        return True
    if f.endswith('asc'):
        return True
    if f.endswith('lastUpdated'):
        return True
    return False


def get_file_repos_info(local_repo, files):
    for f in files:
        root, file = f.rsplit('/', 1)
        remote_repositories = path.join(root, '_remote.repositories')
        if exists(remote_repositories):
            yield (remote_repositories,
                   root[len(local_repo):],
                   (file,))


def get_repos_info(local_repo):
    for root, dirs, files in walk(local_repo):
        if files and '_remote.repositories' in files:
            yield (path.join(root, '_remote.repositories'),
                   root[len(local_repo):],
                   [f for f in files
                    if not excluded(f)])


def parse_remote_repos(remote_repositories, remotes):
    with open(remote_repositories, 'rt', encoding='utf-8') as f:
        lines = [l for l in f.read().splitlines() if not l.startswith('#')]
        return {k: remotes.get(v.replace('=', ''), None) for k, v in
                [l.split('>') for l in lines]}


def create_commands(remote_dict, artifact_path, artifacts):
    def create_artifact_command(artifact):
        extension = artifact.rsplit('.', 1)[1]
        remote_dict_key = artifact[:-(len(extension) + 1)] if extension in [
            'sha1', 'md5', 'sha256'] else artifact

        remote_url = remote_dict.get(remote_dict_key, None)
        if remote_url:
            if remote_url.endswith('/'):
                remote_url = remote_url[:-1]
            rel_path = f'{artifact_path}/{artifact}'
            return f'curl -o "{rel_path}" {remote_url}/{rel_path}'
        else:
            return None

    mkdir_commands = [f'mkdir -p "{artifact_path}"']
    download_commands = [create_artifact_command(artifact) for artifact in
                         artifacts]
    return mkdir_commands + download_commands if any(download_commands) else []


def create_urls(remote_dict, artifact_path, artifacts):
    def create_artifact_urls(artifact):
        extension = artifact.rsplit('.', 1)[1]
        remote_dict_key = artifact[:-(len(extension) + 1)] if extension in [
            'sha1', 'md5', 'sha256'] else artifact

        remote_url = remote_dict.get(remote_dict_key, None)
        if remote_url:
            if remote_url.endswith('/'):
                remote_url = remote_url[:-1]
            rel_path = f'{artifact_path}/{artifact}'
            return f'{remote_url}/{rel_path}'
        else:
            return f'No url found for: {artifact_path}/{artifact}'

    urls = [create_artifact_urls(artifact) for artifact in artifacts]
    return urls if any(urls) else []


def main(settings_file, urls_only, skipped, files=None):
    skipped_artifacts = []
    local_repo, remotes = get_settings_info(settings_file)

    repos_info = get_file_repos_info(local_repo, files) if files else get_repos_info(local_repo)
    for remote_repos, artifact_path, artifacts in repos_info:
        remote_dict = parse_remote_repos(remote_repos, remotes)

        params = [remote_dict, artifact_path, artifacts]
        outputs = create_urls(*params) if urls_only else create_commands(
            *params)

        if outputs:
            for c in outputs:
                print(c)
        else:
            skipped_artifacts.append(artifact_path)

    if skipped:
        for s in skipped_artifacts:
            print('# Skipped:', s)


def parse_args(args):
    parser = ArgumentParser(
        description='Print download commands (POSIX) to enable making '
                    'a remote repo based on the content of a local')
    parser.add_argument(
        'settings_file', help='Settings file')
    parser.add_argument(
        '-u', '--urls_only', help='Print only urls', action='store_true')
    parser.add_argument(
        '-s', '--skipped', help='Print skipped artifacts', action='store_true')
    parser.add_argument(
        '-f', '--files', nargs='*', help='Only for specified files and not all in local_repo')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
