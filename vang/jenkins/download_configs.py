#!/usr/bin/env python3

import argparse
from os import environ, makedirs
from sys import argv

from requests import get

from vang.core.core import pmap_unordered


def get_default_jenkins_spec():
    return {
        'url': environ.get('JENKINS_REST_URL', None),
        'username': environ.get('JENKINS_USERNAME', None),
        'password': environ.get('JENKINS_PASSWORD', None),
        'verify_certificate': not environ.get('JENKINS_IGNORE_CERTIFICATE', None),
    }


def create_params(jenkins_spec):
    return {
        'auth': (jenkins_spec['username'], jenkins_spec['password']),
        'verify': jenkins_spec['verify_certificate']
    }


def get_config(job_name, jenkins_spec):
    params = create_params(jenkins_spec)
    params['url'] = f'{jenkins_spec["url"]}/job/{job_name}/config.xml'
    response = get(**params)
    response.raise_for_status()
    return response.status_code, response.text


def get_output_file(output_dir, job_name):
    return f'{output_dir}/{job_name}/config.xml'


def save(output_file, config):
    with open(output_file, 'wt', encoding='utf-8') as f:
        f.write(config)


def download_config(output_dir, job_name, jenkins_spec):
    try:
        makedirs(f'{output_dir}/{job_name}', exist_ok=True)
        save(get_output_file(output_dir, job_name), get_config(job_name, jenkins_spec)[1])
        return job_name
    except IOError as e:
        return f'{job_name}: {e}'


def download_configs(output_dir, job_names, jenkins_spec=get_default_jenkins_spec(), max_processes=10):
    yield from pmap_unordered(
        lambda job_name: download_config(output_dir, job_name, jenkins_spec),
        job_names,
        max_processes
    )


def get_all_job_names(jenkins_spec=get_default_jenkins_spec(), max_processes=10):
    params = create_params(jenkins_spec)
    params['url'] = f'{jenkins_spec["url"]}/api/json'
    response = get(**params)
    response.raise_for_status()
    return [job['name'] for job in response.json()['jobs']]


def parse_args(args):
    parser = argparse.ArgumentParser(description='Download Jenkins configs')
    parser.add_argument('output_dir', help='The dir to save configs in')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--job_names', nargs='+', help='Name of the jobs for which to download configs')
    group.add_argument('-a', '--all', action='store_true', help='Download all configs')
    return parser.parse_args(args)


def main(output_dir, job_names, all):
    for job_name in download_configs(output_dir, get_all_job_names() if all else job_names):
        print(job_name)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
