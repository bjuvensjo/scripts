#!/usr/bin/env python3
from argparse import ArgumentParser
from glob import glob
from itertools import product
from os.path import realpath, normpath
from pathlib import Path
from subprocess import PIPE, STDOUT, run
from sys import argv

from vang.pio.shell import run_commands


def get_work_dirs(find, root):
    return [
        Path(realpath(p)).parent for p in glob(
            normpath('{}/**/{}'.format(root, find)),
            recursive=True,
        )
    ]


def get_command(commands):
    return [' && '.join(commands)]


def execute_in_parallel(root, commands, find='.git/'):
    commands_and_work_dirs = tuple(
        product(
            get_command(commands),
            get_work_dirs(find, root),
        ))
    yield from run_commands(commands_and_work_dirs, max_processes=25, check=False)


def execute_in_sequence(root, commands, find='.git/', timeout=None):
    command = get_command(commands)[0]
    for cwd in get_work_dirs(find, root):
        yield run(
            command,
            cwd=cwd,
            stdout=PIPE,
            stderr=STDOUT,
            check=False,
            timeout=timeout,
            shell=True)


def main(root, commands, find='.git/', sequence=False):
    execute = execute_in_sequence if sequence else execute_in_parallel
    for process in execute(root, commands, find):
        print(process.stdout.decode(errors="ignore").strip())


def parse_args(args):
    parser = ArgumentParser(
        description='Execute commands recursively (default in git repositories)'
    )
    parser.add_argument('commands', nargs='+', help='Commands')
    parser.add_argument('-r', '--root', help='The root directory', default='.')
    parser.add_argument(
        '-f',
        '--find',
        help='The file/dir to be in the directory in which to execute, '
        'default ".git/"',
        default='.git/')
    parser.add_argument(
        '-s',
        '--sequence',
        help='Run the commands in sequence, i.e. not in parallel',
        action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.root, args.commands, args.find, args.sequence)
