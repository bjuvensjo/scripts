#!/usr/bin/env python3
from os.path import basename
from sys import argv

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}'.format(project, repo) + \
           '/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled'


def enable_web_hook(repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = '{"hook-url-0":"http://10.46.64.31:8001/cgi-bin/webhook/"}'
        yield spec, call(uri, request_data, "PUT")


if __name__ == '__main__':
    if '-d' in argv and len(argv) > 1:
        dirs = ['.'] if len(argv) == 2 else [arg for arg in argv[1:] if arg != '-d']
        specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]
    elif len(argv) == 3:
        specs = [[argv[1], argv[2]]]
    else:
        print('Usage: {} [-d dirs] | [project repo]'.format(basename(__file__)))
        exit(1)

    for spec, response in enable_web_hook(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], 'enabled' if response['enabled'] else ' not enabled'))
