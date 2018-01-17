#!/usr/bin/env python3
import traceback

from bb_get_clone_urls import get_clone_urls
from shell import run_commands


def clone_projects(keys, root_dir):
    yield from run_commands([('git clone {} {}/{}'.format(cmd[2], cmd[0], '/'.join(cmd[1].split('.'))), root_dir)
                             for cmd in get_clone_urls(keys)], max_processes=25, timeout=20)


def main(keys, root_dir):
    n = 1
    for process in clone_projects(keys, root_dir):
        try:
            print(str(n).zfill(2), process.stdout.read().decode(), end='')
            n += 1
        except:
            print(traceback.format_exc())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clone Bitbucket projects')
    parser.add_argument('keys', nargs='+', help='Project keys')
    parser.add_argument('-d', '--dir', default='.', help='The directory to clone into')
    args = parser.parse_args()

    main(args.keys, args.dir)
