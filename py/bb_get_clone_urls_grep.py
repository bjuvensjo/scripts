#!/usr/bin/env python3
import re

from bb_get_clone_urls import get_all_clone_urls
from bb_get_projects import get_all_projects


def get_clone_urls_grep(patterns):
    return get_all_clone_urls([p['key'] for p in get_all_projects()
                               if any((re.match(r'{}'.format(pattern), p['key']) for pattern in patterns))])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get clone urls for project patterns from Bitbucket.')
    parser.add_argument('patterns', nargs='+', help='The patterns.')
    parser.add_argument('-c', '--command', help='Print as clone commands', action='store_true')
    args = parser.parse_args()

    for project, repo, clone_url, in get_clone_urls_grep(args.patterns):
        clone_dir = '{}/{}'.format(project, repo.replace('.', '/'))
        print('git clone {} {}'.format(clone_url, clone_dir) if args.command else clone_url)
