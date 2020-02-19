#!/usr/bin/env python3

import argparse
from importlib import import_module
from sys import argv

from vang.jenkins.copy_job import copy_job


def copy_jobs(jobs, from_jenkins_spec, to_jenkins_spec, replacements=[]):
    for job in jobs:
        from_name = None
        to_name = None
        job_replacements = replacements
        try:
            if type(job) is str:
                to_name = from_name = job
            elif type(jobs) is list and len(job) == 2:
                from_name, to_name = job
            elif type(jobs) is list and len(job) == 3:
                from_name, to_name, job_replacements = job

            if type(from_name) != str or type(to_name) != str or not (
                    type(job_replacements) is list or callable(job_replacements)):
                raise ValueError('job must be a string, a pair of strings or a pair of string and a callable')

            response_code = copy_job(from_name, to_name, from_jenkins_spec, to_jenkins_spec, job_replacements)
            print('Created copy' if response_code == 200 else 'Failed to create copy', to_name, response_code)
        except IOError as r:
            print('IOError while trying to create copy', to_name, r)
        except ValueError as v:
            print('ValueError while trying to create copy', to_name, v)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Copy Jenkins jobs, possibly between Jenkins instances')
    parser.add_argument('-c', '--config_path', default='vang.jenkins.copy_jobs_config',
                        help='The configuration path')
    return parser.parse_args(args)


def main(config_path):
    config = import_module(config_path)
    copy_jobs(config.jobs, config.from_jenkins_spec, config.to_jenkins_spec, config.replacements)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
