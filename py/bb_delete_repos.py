#!/usr/bin/env python3
from multiprocessing.dummy import Pool

from bb_api import call
from bb_utils import get_repo_specs


def delete_repo(spec):
    return spec, call('/rest/api/1.0/projects/{}/repos/{}'.format(spec[0], spec[1]), method="DELETE")


def delete_repos(repo_specs, max_processes=10):
    with Pool(processes=max_processes) as pool:
        return pool.map(delete_repo, repo_specs)


def main(dirs=['.'], repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, response in delete_repos(specs):
        print('{}/{}: {}'.format(spec[0], spec[1], response))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Delete Bitbucket repos')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*',
                       help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.dirs, args.repos, args.projects)
