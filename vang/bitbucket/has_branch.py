#!/usr/bin/env python3

from vang.bitbucket.get_branches import get_branches
from vang.bitbucket.utils import get_repo_specs


def has_branch(repo_specs, branch):
    for spec in repo_specs:
        branches = [b['displayId'] for spec, bs in get_branches((spec,), branch) for b in bs]
        yield spec, branch in branches


def main(branch, only_has=True, only_not_has=False, dirs=None, repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, has in has_branch(specs, branch):
        if only_has:
            if has:
                print('{}/{}'.format(spec[0], spec[1]))
        elif only_not_has:
            if not has:
                print('{}/{}'.format(spec[0], spec[1]))
        else:
            print('{}/{}, {}: {}'.format(spec[0], spec[1], branch, has))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Check repository branches in Bitbucket')
    parser.add_argument('branch', help='The branch to check')
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument('-o', '--only_has', action='store_true', help='Print only repos that has the branch.')
    filter_group.add_argument('-n', '--only_not_has', action='store_true',
                              help='Print only repos that not has the branch.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.branch, args.only_has, args.only_not_has, args.dirs, args.repos, args.projects)
