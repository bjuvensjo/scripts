#!/usr/bin/env python3
from json import dumps
from multiprocessing.dummy import Pool

from itertools import product

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


def enable_repo_web_hook(spec, url):
    uri = '/rest/api/1.0/projects/{}/repos/{}'.format(spec[0], spec[1]) + \
          '/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled'
    request_data = dumps({'hook-url-0': url})
    return spec, call(uri, request_data, 'PUT')


def enable_web_hook(repo_specs, url, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(enable_repo_web_hook, product(repo_specs, [url]))


def main(url, dirs=['.'], repos=None):
    if args.repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in enable_web_hook(specs, url):
        print('{}/{}: {}'.format(spec[0], spec[1], 'enabled' if response['enabled'] else ' not enabled'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Enables Bitbucket webhook.')
    parser.add_argument('url',
                        help='The url which to send repo info to, e.g. http://10.20.30.40:8002/wildcat/webhook/')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from.')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    args = parser.parse_args()

    main(args.url, args.dirs, args.repos)
