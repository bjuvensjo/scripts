#!/usr/bin/env python3

import argparse
from os import environ
from sys import argv

from requests import post

from vang.jenkins.download_configs import get_config


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


def create_job(jenkins_spec, name, config):
    params = create_params(jenkins_spec)
    params['url'] = f'{jenkins_spec["url"]}/createItem?name={name}'
    params['data'] = config
    params['headers'] = {'Content-Type': 'application/xml'}
    response = post(**params)
    return response.status_code


def update_config(config, replacements):
    if callable(replacements):
        return replacements(config)
    else:
        for r in replacements:
            config = config.replace(*r)
        return config


def copy_job(from_name, to_name, from_jenkins_spec=get_default_jenkins_spec(),
             to_jenkins_spec=get_default_jenkins_spec(), replacements=None):
    from_response_code, from_config = get_config(from_name, from_jenkins_spec)
    to_config = update_config(from_config, replacements)
    to_response_code = create_job(to_jenkins_spec, to_name, to_config)
    return {
        'from_name': from_name,
        'to_name': to_name,
        'from_config': from_config,
        'to_config': to_config,
        'response_code': to_response_code,
    }


def parse_args(args):
    parser = argparse.ArgumentParser(description='Copy Jenkins job')
    parser.add_argument('from_name', help='Name of job to copy')
    parser.add_argument('to_name', help='Name of job copy')
    parser.add_argument('-r', '--replacements', nargs='*', default=[],
                        help='Pair of replacements, e.g. old1 new1 old2 new2')
    return parser.parse_args(args)


def main(from_name, to_name, replacements=()):
    response = copy_job(from_name, to_name, replacements=zip(replacements[0::2], replacements[1::2]))
    response_code = response['response_code']
    print('Created' if response_code == 200 else 'Failed to create', to_name, response_code)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
