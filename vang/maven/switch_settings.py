#!/usr/bin/env python3
import argparse
from os import environ, name
from os.path import exists
from sys import argv

from vang.pio.shell import run_command


def switch_settings(ending):
    source = f'{environ["HOME"]}/.m2/settings_{ending}.xml'
    if not exists(source):
        raise ValueError(f'{source} does not exist')
    target = f'{environ["HOME"]}/.m2/settings.xml'
    return run_command(f'ln -sf {source} {target}', True)


def main(ending):
    if name == 'posix':
        rc, output = switch_settings(ending)
        print(output)
    else:
        print(
            'Platform not supported. Please implement, and make a pull request.'
        )


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Switch maven settings in ~/.m2')
    parser.add_argument(
        'ending',
        help='The ending of the settings file to switch to'
        ', e.g. FOO for ~/.m2/settings_FOO.xml')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
