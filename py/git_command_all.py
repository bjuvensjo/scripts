#!/usr/bin/env python3
from glob import glob
from os.path import realpath
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT

from util import chunks


def execute(dirs, commands, max_processes=10):
    if len(dirs) > max_processes:
        for chunk in chunks(dirs, max_processes):
            yield from execute(chunk, commands, max_processes=max_processes)
    else:
        joined_commands = ' && '.join(commands)
        for dir in dirs:
            process = Popen(joined_commands, stdout=PIPE, stderr=STDOUT, shell=True, cwd=dir)
            yield process.stdout.read().decode().strip()


def execute_recursively(root, commands):
    return execute([Path(realpath(p)).parent for p in glob("{}/**/.git/".format(root), recursive=True)], commands)


def main(root, commands):
    for response in execute_recursively(root, commands):
        print(response)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute commands recursively in git repositories')
    parser.add_argument('commands', nargs='+', help='Commands')
    parser.add_argument('-r', '--root', default='.')
    args = parser.parse_args()

    main(args.root, args.commands)
