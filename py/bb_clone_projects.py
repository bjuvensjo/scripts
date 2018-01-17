#!/usr/bin/env python3
import traceback

from bb_get_clone_urls import get_clone_urls
from shell import run_commands


def clone_projects(keys):
    yield from run_commands(['git clone {} {}/{}'.format(cmd[2], cmd[0], '/'.join(cmd[1].split('.')))
                             for cmd in get_clone_urls(keys)], cwd='.', max_processes=25, timeout=20)


def main(keys):
    n = 1
    for process in clone_projects(keys):
        try:            
            print(str(n).zfill(2), process.stdout.read().decode(), end='')
            n += 1
        except:
            print(traceback.format_exc())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clone Bitbucket projects')
    parser.add_argument('keys', nargs='+', help='Project keys')
    args = parser.parse_args()

    main(args.keys)
