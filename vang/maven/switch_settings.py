#!/usr/bin/env python3
import argparse
from os import environ, name
from sys import argv

from vang.pio.shell import run_command


def switch_settings(ending):
    return run_command('ln -sf settings_{}.xml settings.xml'.format(ending), True, '{}/.m2'.format(environ['HOME']))


def main(ending):
    if name == 'posix':
        rc, output = switch_settings(ending)
        print(output)
    else:
        print('Platform not supported. PLease implement, and make a pull request.')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Switch maven settings in ~/.m2')
    parser.add_argument('ending',
                        help='The ending of the settings file to switch to, e.g. FOO for ~/.m2/settings_FOO.xml')
    return parser.parse_args(args)


if __name__ == '__main__':
    main(**parse_args(argv[1:]).__dict__)
