#!/usr/bin/env python3

import argparse
from glob import glob
from os import environ
from os.path import realpath, normpath
from pathlib import Path
from sys import argv

from requests import post

from vang.core.core import pmap_unordered
from vang.jenkins.download_configs import get_all_job_names


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


def post_config(job_name, config, update, jenkins_spec):
    update_uri = f'job/{job_name}/config.xml'
    create_uri = f'createItem?name={job_name}'

    params = create_params(jenkins_spec)
    params['url'] = f'{jenkins_spec["url"]}/{update_uri if update else create_uri}'
    params['data'] = config
    params['headers'] = {'Content-Type': 'application/xml'}

    response = post(**params)
    response.raise_for_status()
    return response.status_code, response.text


def get_input_file(input_dir, job_name):
    return f'{input_dir}/{job_name}/config.xml'


def read(file_path):  # pragma: no cover
    with open(file_path, 'rt', encoding='utf-8') as f:
        return f.read()


def get_configs_paths(input_dir):
    return [Path(normpath(realpath(p))) for p in glob(f'{input_dir}/**/config.xml', recursive=True)]


def upload_config(config_path, existing_job_names, jenkins_spec):
    job_name = config_path.parent.name
    try:
        config = config_path.read_text('utf-8')
        post_config(job_name, config, job_name in existing_job_names, jenkins_spec)
        return job_name
    except IOError as e:
        return f'{job_name}: {e}'


def upload_configs(input_dir, jenkins_spec=get_default_jenkins_spec(), max_processes=10):
    existing_job_names = get_all_job_names(jenkins_spec)
    yield from pmap_unordered(
        lambda config_path: upload_config(config_path, existing_job_names, jenkins_spec),
        get_configs_paths(input_dir),
        max_processes
    )


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Upload Jenkins configs, i.e. update existing jobs and create non existing')
    parser.add_argument('input_dir', help='The dir to load configs from.')
    return parser.parse_args(args)


def main(input_dir):
    for job_name in upload_configs(input_dir, get_default_jenkins_spec()):
        print(job_name)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
