#!/usr/bin/env python3

import datetime
import traceback
from os import makedirs
from shutil import rmtree
from urllib.error import HTTPError

from vang.bitbucket.api import call
from vang.bitbucket.clone_repos import clone, get_repos_commands
from vang.bitbucket.get_repos import get_all_repos
from vang.core.core import pmap_unordered


def to_date(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp / 1000)


def get_commit_author_dates(repos_specs, branch):
    def f(spec):
        project, repo = spec
        try:
            commits = call(
                '/rest/api/1.0/projects/{}/repos/{}/commits?limit={}&until={}'.
                format(project, repo, 1, branch))
            author_timestamp = commits['values'][0]['authorTimestamp']
        except HTTPError:
            # Does not have branch
            author_timestamp = None
        return spec, to_date(author_timestamp) if author_timestamp else None

    return pmap_unordered(f, repos_specs)


def get_repos_with_commits_since(branch, projects, since):
    return [
        spec for spec, author_date in get_commit_author_dates(
            get_all_repos(projects, only_spec=True),
            branch,
        ) if author_date and author_date > since
    ]


def clone_repos(commands, clone_dir):
    rmtree(clone_dir, ignore_errors=True)
    makedirs(clone_dir)
    n = 1
    for process in clone(
        [command for clone_dir, project, repo, command in commands],
            clone_dir,
    ):
        try:
            print(
                str(n).zfill(2),
                process.returncode,
                process.stdout.decode(),
                end='')
            n += 1
        except OSError:
            print(traceback.format_exc())


def main(since, projects, branch, clone_dir):
    repo_specs = get_repos_with_commits_since(branch, projects, since)
    commands = get_repos_commands(['{}/{}'.format(p, r) for p, r in repo_specs],
                                  branch, True)
    for c in commands:
        print(c[3])
    clone_repos(commands, clone_dir)


if __name__ == '__main__':
    since = datetime.datetime(2018, 1, 1)
    projects = ['ESBU', 'ESBES']
    # branch = 'develop'
    # clone_dir = '/Users/ei4577/slask/crap/develop'
    branch = 'feature/bosse'
    clone_dir = '/Users/ei4577/slask/crap/bosse'

    main(since, projects, branch, clone_dir)
