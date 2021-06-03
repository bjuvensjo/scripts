#!/usr/bin/env python3
import argparse
from sys import argv

from vang.bitbucket.get_branches import get_all_branches
from vang.bitbucket.get_projects import get_projects_page
from vang.bitbucket.get_repos import get_repos_page
from vang.bitbucket.get_tags import get_all_tags
from vang.core.core import pmap_unordered


def projects(max_nb_projects=None):
    count = -1
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_projects_page(limit, start)

        if size:
            for value in values:
                count = count + 1
                if max_nb_projects and count == max_nb_projects:
                    return value
                else:
                    yield value


def repos(project, max_nb_projects=None):
    count = -1
    limit = 25
    start = 0
    is_last_page = False

    while not is_last_page:
        size, values, is_last_page, start = get_repos_page(
            project, limit, start)

        if size:
            for value in values:
                count = count + 1
                result = (value['project']['key'], value['slug'])
                if max_nb_projects and count == max_nb_projects:
                    return result
                else:
                    yield result


def branches(repo):
    return get_all_branches(repo)


def tags(repo):
    return get_all_tags(repo)


def validate_repos(project, max_repos=None):
    valid = []
    corrupt = []
    for r in repos(project, max_repos):
        s = "/".join(r)
        try:
            branches(r)
            tags(r)
            valid.append(s)
        except KeyError:
            corrupt.append(s)
    return valid, corrupt


def validate_projects(max_projects=None, max_repos=None, max_processes=10):
    for valid, corrupt in pmap_unordered(
            lambda p: validate_repos(p['key'], max_repos),
            projects(max_projects),
            processes=max_processes):
        for v in valid:
            print(f'{v} is OK')
        for c in corrupt:
            print(f'{c} is CORRUPT')


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Validate projects by checking that the rest api can be used to retrieve repos, branches and tags.')
    parser.add_argument('-p', '--max_projects', help='Maximum number of projects', type=int, default=None)
    parser.add_argument('-r', '--max_repos', help='Maximum number of repos', type=int, default=None)
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    validate_projects(**parse_args(argv[1:]).__dict__)
