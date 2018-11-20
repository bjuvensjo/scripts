#!/usr/bin/env python3

from vang.bitbucket.get_repos import get_all_repos
from vang.pio.shell import run_command


def get_branch(git_dir):
    return run_command('git rev-parse --abbrev-ref HEAD', True, git_dir)[1]


def get_clone_url(git_dir):
    return_code, url = run_command(
        f'git --git-dir {git_dir} remote get-url origin',
        True,
        git_dir,
        False,
    )
    if return_code:
        return run_command(
            f'git --git-dir {git_dir}/.git remote get-url origin',
            True,
            git_dir,
        )[1]
    else:
        return url


def get_project_and_repo(git_dir):
    project, repo = get_clone_url(git_dir)[:-4].split('/')[-2:]
    return project.upper(), repo


def get_repo_specs(dirs=None, repos=None, projects=None):
    if projects:
        return get_all_repos(projects, only_spec=True, max_processes=10)
    elif repos:
        return (tuple(repo.split('/')) for repo in repos)
    else:
        return (get_project_and_repo(a_dir) for a_dir in dirs)
