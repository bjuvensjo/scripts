#!/usr/bin/env python3

from json import dumps
from multiprocessing.dummy import Pool

from itertools import chain, product

from bb_api import call
from bb_utils import get_clone_url, get_project_and_repo


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
        return chain(pool.starmap(fork_repo, product(repo_specs, [fork_project])))


def main(dirs=['.'], repos=None):
    if repos:
        specs = (repo.split('/') for repo in repos)
    else:
        specs = (get_project_and_repo(get_clone_url(dir)) for dir in dirs)
    for spec, response in fork_repos(specs, args.fork_project):
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
    args = parser.parse_args()

    main(args.dirs, args.repos)
