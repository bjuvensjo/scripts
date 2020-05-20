#!/usr/bin/env python3
import argparse
from itertools import product
from multiprocessing.dummy import Pool
from sys import argv

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs

hook_template = {
    "title": None,
    "url": None,
    "committersToIgnore": "",
    "branchesToIgnore": "",
    "enabled": True,
    "tagCreated": False,
    "branchDeleted": False,
    "branchCreated": False,
    "repoPush": True,
    "prDeclined": False,
    "prRescoped": False,
    "prMerged": False,
    "prReopened": False,
    "prUpdated": False,
    "prCreated": False,
    "prCommented": False,
    "buildStatus": False
}


def get_uri(spec):
    return f'/rest/webhook/1.0/projects/{spec[0]}/repos/{spec[1]}/configurations'


def delete_web_hook(spec, hook_id):
    return call(f'{get_uri(spec)}/{hook_id}', only_response_code=True, method='DELETE')


def create_web_hook(spec, hook):
    return call(get_uri(spec), only_response_code=True, method='POST', request_data=hook)


def get_web_hooks(spec):
    return call(get_uri(spec))


def set_repo_web_hooks(spec, hooks):
    try:
        # Delete existing web hooks
        for hook in get_web_hooks(spec):
            delete_response_code = delete_web_hook(spec, hook['id'])
            if delete_response_code != 204:
                return spec, False, f'Can not delete {hook["id"]}: {delete_response_code}'

        # Create web hooks
        for hook in hooks:
            create_response_code = create_web_hook(spec, hook)
            if create_response_code != 200:
                return spec, False, f'Can not create {hook}: {create_response_code}'

        return spec, True, f'Set webhooks {hooks}'
    except IOError as ioe:
        return spec, False, ioe


def set_web_hooks(specs, hooks, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(set_repo_web_hooks, product(specs, (hooks,)))


def main(title, url, dirs, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    hook = dict(hook_template, title=title, url=url)
    hooks = (hook,)
    for spec, result, message in set_web_hooks(specs, hooks):
        if result:
            print(f'spec[0]/{spec[1]}: {result}')
        else:
            print(f'{spec[0]}/{spec[1]}: {result} {message}')


def parse_args(args):
    parser = argparse.ArgumentParser(description='Set Bitbucket webhooks. '
                                                 'The hooks are based on a template defined in this script.')
    parser.add_argument('title', help='The webhook title')
    parser.add_argument('url', help='The webhook url')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from.')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
