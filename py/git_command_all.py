#!/usr/bin/env python3
from glob import glob
from os.path import realpath, normpath
from pathlib import Path

from itertools import product

from shell import run_commands


def execute(root, commands):
    cwds = [Path(realpath(p)).parent for p in glob(normpath('{}/**/.git/'.format(root)), recursive=True)]
    command = [' && '.join(commands)]
    commands_and_cwds = tuple(product(command, cwds))

    yield from run_commands(commands_and_cwds, max_processes=25)


def main(root, commands):
    for process in execute(root, commands):
        print(process.stdout.read().decode().strip())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute commands recursively in git repositories')
    parser.add_argument('commands', nargs='+', help='Commands')
    parser.add_argument('-r', '--root', default='.')
    args = parser.parse_args()

    main(args.root, args.commands)
