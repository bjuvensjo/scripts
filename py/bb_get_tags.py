#!/usr/bin/env python3
from multiprocessing.dummy import Pool

from itertools import product

from bb_api import call
from bb_utils import get_repo_specs


def get_repo_tags(spec, tag=''):
    return spec, call('/rest/api/1.0/projects/{}/repos/{}/tags?filterText={}'.format(spec[0], spec[1], tag))


def get_tags(repo_specs, tag='', max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.starmap(get_repo_tags, product(repo_specs, [tag]))


def main(tag='', dirs=['.'], repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in get_tags(specs, tag):
        print('{}/{}: {}'.format(spec[0], spec[1], [value['displayId'] for value in response['values']]))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get repository tags from Bitbucket')
    parser.add_argument('-t', '--tag',
                        help='Tag filter',
                        default='')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.tag, args.dirs, args.repos, args.projects)
