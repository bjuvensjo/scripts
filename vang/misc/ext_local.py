#!/usr/bin/env python3
from argparse import ArgumentParser
from shutil import copy2
from sys import argv

from vang.misc.mac_ip import get_ip_address

etc_hosts_file = '/etc/hosts'
encoding = 'utf-8'


def update(backup=None):
    if backup:
        copy2(etc_hosts_file, backup)

    with open(etc_hosts_file, 'rt', encoding=encoding) as f:
        updated_entries = '\n'.join([f'{get_ip_address()}\text.local' if '\text.local' in l else l
                                     for l in f.read().splitlines()])

    with open(etc_hosts_file, 'wt', encoding=encoding) as f:
        f.write(updated_entries)

    return updated_entries


def parse_args(args):
    parser = ArgumentParser(
        description='Update ext.local entry in /etc/hosts to the current ip address.'
                    'Run it with sudo or give yourself write permission to the etc/hosts file and run it without sudo.')
    parser.add_argument(
        '-b', '--backup', help='Backup etc/hosts in this file', default=None)
    return parser.parse_args(args)


if __name__ == '__main__':
    params = parse_args(argv[1:])
    print(update(params.backup))
