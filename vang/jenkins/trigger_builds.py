#!/usr/bin/env python3

import argparse
from sys import argv

from vang.jenkins.api import call


def trigger_builds(names):
    return [(name, call(
        f'/job/{name}/build',
        method='POST',
        only_response_code=True,
    )) for name in names]


def parse_args(args):
    parser = argparse.ArgumentParser(description='Trigger Jenkins jobs')
    parser.add_argument(
        'job_names',
        nargs='+',
        help='Jenkins job names',
    )
    return parser.parse_args(args)


if __name__ == '__main__':
    pargs = parse_args(argv[1:])
    for job_name, response_code in trigger_builds(pargs.job_names):
        print(job_name, response_code)
