#!/usr/bin/env python3

from bb_get_clone_urls import get_all_clone_urls
from shell import run_commands


def clone_projects(keys):
    # TODO Parallelize get_all_repos in get_all_clone_urls
    yield from run_commands(['git clone {} {}/{}'.format(cmd[2], cmd[0], '/'.join(cmd[1].split('.')))
                             for cmd in get_all_clone_urls(keys)], max_processes=10, cwd='.')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clone projects.')
    parser.add_argument('keys', nargs='+', help='Bitbucket project keys.')
    args = parser.parse_args()

    for process in clone_projects(args.keys):
        print(process.stdout.readline().decode(), end='')
