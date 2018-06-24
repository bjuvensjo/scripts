#!/usr/bin/env python3

from json import dumps
from multiprocessing.dummy import Pool

from itertools import product

from vang.bitbucket.api import call
from vang.bitbucket.utils import get_repo_specs


def fork_repo(spec, fork_project):
    uri = '/rest/api/1.0/projects/{}/repos/{}'.format(spec[0], spec[1])
    request_dict = {
        'slug': spec[1],
        'project': {
            'key': fork_project
        }
    }

    request_data = dumps(request_dict)
    return spec, call(uri, request_data, 'POST')


def fork_repos(repo_specs, fork_project, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(fork_repo, product(repo_specs, [fork_project]))


def main(fork_project, dirs, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in fork_repos(specs, fork_project):
        print('{}/{}: {}'.format(spec[0], spec[1], response))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fork Bitbucket repos')
    parser.add_argument('fork_project', help='Fork project')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.fork_project, args.dirs, args.repos, args.projects)
