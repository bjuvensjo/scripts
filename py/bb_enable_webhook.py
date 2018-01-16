#!/usr/bin/env python3
from json import dumps

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return '/rest/api/1.0/projects/{}/repos/{}'.format(project, repo) + \
           '/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled'


def enable_web_hook(url, repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = dumps({'hook-url-0': url})
        yield spec, call(uri, request_data, 'PUT')


def main(url, dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in enable_web_hook(url, specs):
        print('{}/{}: {}'.format(spec[0], spec[1], 'enabled' if response['enabled'] else ' not enabled'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Enables Bitbucket webhook.')
    parser.add_argument('-u', '--url',
                        help='The url which to send repo info to, e.g. http://10.20.30.40:8002/wildcat/webhook/',
                        required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from.')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.url, args.dirs, args.repos)
