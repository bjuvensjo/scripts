#!/usr/bin/env python3
import argparse
from sys import argv

from vang.tfs.api import call


def delete_repo(repo):
    organisation, project, name = repo.split('/')
    repo_id = call(
        f'/{organisation}/{project}/_apis/git/repositories/{name}?api-version=3.2',
        method='GET',
    )['id']
    return call(
        f'/{organisation}/{project}/_apis/git/repositories/{repo_id}?api-version=3.2',
        method='DELETE',
        only_response_code=True
    )


def main(repo):
    response = delete_repo(repo)
    print(response)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Delete TFS repository')
    parser.add_argument(
        'repo',
        help='The TFS repository to delete, e.g. organisation/project/repo1')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
