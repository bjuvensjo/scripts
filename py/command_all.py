#!/usr/bin/env python3
from glob import glob
from itertools import product
from os.path import realpath, normpath
from pathlib import Path
from shlex import split
from subprocess import Popen, PIPE, STDOUT

from shell import run_commands


def get_work_dirs(find, root):
    return [Path(realpath(p)).parent for p in glob(normpath('{}/**/{}'.format(root, find)), recursive=True)]


def get_command(commands):
    return [' && '.join(commands)]


def execute_in_parallel(root, commands, find='.git/'):
    commands_and_work_dirs = tuple(product(get_command(commands), get_work_dirs(find, root)))
    yield from run_commands(commands_and_work_dirs, max_processes=25)


def execute_in_sequence(root, commands, find='.git/'):
    command = get_command(commands)[0]
    for cwd in get_work_dirs(find, root):
        yield Popen(split(command), stdout=PIPE, stderr=STDOUT, cwd=cwd)


def main(root, commands, find='.git/', sequence=False):
    execute = execute_in_sequence if sequence else execute_in_parallel
    for process in execute(root, commands, find):
        print(process.stdout.read().decode().strip())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute commands recursively (default in git repositories)')
    parser.add_argument('commands', nargs='+', help='Commands')
    parser.add_argument('-r', '--root', help='The root directory', default='.')
    parser.add_argument('-f', '--find', help='The file/dir to be in the directory in which to execute, default ".git/"',
                        default='.git/')
    parser.add_argument('-s', '--sequence', help='Run the commands in sequence, i.e. not in parallel',
                        action='store_true')
    args = parser.parse_args()

    main(args.root, args.commands, args.find, args.sequence)
