#!/usr/bin/env python3
import argparse
import sys

from vang.bitbucket.api import get_all


def get_commits(spec, branch, take):
    return get_all(f'/rest/api/1.0/projects/{spec[0]}/repos/{spec[1]}/commits',
                   {'until': branch},
                   take)


def main(repo, branch, take):
    spec = repo.split('/')
    for commits in get_commits(spec, branch, take if take > 0 else sys.maxsize):
        print(commits)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get repository commits from Bitbucket')
    parser.add_argument('repo', help='Repo, e.g. key1/repo1')
    parser.add_argument('branch', help='branch')
    parser.add_argument('--take', '-t', type=int,
                        help='The number of commit from and including HEAD. -1 for all commits',
                        default=sys.maxsize)
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(sys.argv[1:]).__dict__)
