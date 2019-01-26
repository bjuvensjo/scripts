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

    if any(['ext.local' in l for l in original_lines]):
        updated_lines = [
            f'{get_ip_address()}   ext.local\n' if 'ext.local' in l else l
            for l in original_lines
        ]
    else:
        updated_lines = list(original_lines)
        if not updated_lines[-1].endswith('\n'):
            updated_lines[-1] = updated_lines[-1] + '\n'
        updated_lines.append(f'{get_ip_address()}   ext.local\n')

    if updated_lines != original_lines:
        with open(etc_hosts_file, 'wt', encoding=encoding) as f:
            f.writelines(updated_lines)

    return updated_lines


def parse_args(args):
    parser = ArgumentParser(
        description=
        'Updates ext.local entry in /etc/hosts to the current ip address.'
        'Run it with sudo or give yourself write permission to the etc/hosts '
        'file and run it without sudo.'
        'To run it automatically, modify ext_local.plist and copy it, load and '
        'start as below: '
        'sudo cp ext_local.plist /Library/LaunchDaemons/com.github.bjuvensjo.scripts.ext_local.plist, '
        'sudo launchctl load /Library/LaunchDaemons/com.github.bjuvensjo.scripts.ext_local.plist, '
        'sudo launchctl start com.github.bjuvensjo.scripts.ext_local')
    parser.add_argument(
        '-b', '--backup', help='Backup etc/hosts in this file', default=None)
    return parser.parse_args(args)


def main(backup):
    print(''.join(update(backup)))


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
