#!/usr/bin/env python3

from sys import argv

from bb_get_repos import get_all_repos


def get_all_clone_urls(keys):
    for repo in get_all_repos(keys):
        yield repo['project']['key'], repo['slug'], repo['links']['clone'][0]['href']


if __name__ == '__main__':
    for project, repo, clone_url, in get_all_clone_urls(argv[1:]):
        clone_dir = '{}/{}'.format(project, repo.replace('.', '/'))
        print('git clone {} {}'.format(clone_url, clone_dir))
