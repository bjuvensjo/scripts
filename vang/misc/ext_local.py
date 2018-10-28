#!/usr/bin/env python3
from argparse import ArgumentParser
from shutil import copy2
from sys import argv

from vang.misc.mac_ip import get_ip_address

etc_hosts_file = '/etc/hosts'
encoding = 'utf-8'


def update(backup_file=None):
    if backup_file:
        copy2(etc_hosts_file, backup_file)

    with open(etc_hosts_file, 'rt', encoding=encoding) as f:
        original_lines = f.readlines()

    updated_lines = [f'{get_ip_address()}\text.local\n' if '\text.local' in l else l
                     for l in original_lines]

    if updated_lines != original_lines:
        with open(etc_hosts_file, 'wt', encoding=encoding) as f:
            f.writelines(updated_lines)

    return updated_lines


def parse_args(args):
    parser = ArgumentParser(
        description='Update ext.local entry in /etc/hosts to the current ip address.'
                    'Run it with sudo or give yourself write permission to the etc/hosts file and run it without sudo.'
                    'To run it automatically, modify ext_local.plist and load and start it with: '
                    'launchctl load ~/Library/LaunchAgents/com.github.bjuvensjo.scripts.vang.misc.ext_local.plist, '
                    'launchctl start com.github.bjuvensjo.scripts.vang.misc.ext_local')
    parser.add_argument(
        '-b', '--backup', help='Backup etc/hosts in this file', default=None)
    return parser.parse_args(args)


if __name__ == '__main__':
    params = parse_args(argv[1:])
    print(''.join(update(params.backup)))
