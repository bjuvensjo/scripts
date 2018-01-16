#!/usr/bin/env python3

from bb_get_repos import get_all_repos


def get_clone_urls(keys):
    for repo in get_all_repos(keys):
        yield repo['project']['key'], repo['slug'], repo['links']['clone'][0]['href']


def main(projects, command):
    for project, repo, clone_url, in get_clone_urls(projects):
        clone_dir = '{}/{}'.format(project, repo.replace('.', '/'))
        print('git clone {} {}'.format(clone_url, clone_dir) if command else clone_url)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get clone urls for projects from Bitbucket.')
    parser.add_argument('projects', nargs='+', help='The projects.')
    parser.add_argument('-c', '--command', help='Print as clone commands', action='store_true')
    args = parser.parse_args()

    main(args.projects, args.command)
