#!/usr/bin/env python3
from glob import glob
from itertools import product
from os.path import realpath, normpath
from pathlib import Path

from shell import run_commands


def execute(root, commands, find='.git/'):
    work_dirs = [Path(realpath(p)).parent for p in glob(normpath('{}/**/{}'.format(root, find)), recursive=True)]
    command = [' && '.join(commands)]
    commands_and_work_dirs = tuple(product(command, work_dirs))

    yield from run_commands(commands_and_work_dirs, max_processes=25)


def main(root, commands, find='.git/'):
    for process in execute(root, commands, find):
        print(process.stdout.read().decode().strip())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute commands recursively (default in git repositories)')
    parser.add_argument('commands', nargs='+', help='Commands')
    parser.add_argument('-r', '--root', help='The root directory', default='.')
    parser.add_argument('-f', '--find', help='The file/dir to be in the directory in which to execute, default ".git/"',
                        default='.git/')
    args = parser.parse_args()

    main(args.root, args.commands, args.find)
