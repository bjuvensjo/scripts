#!/usr/bin/env python3
import shlex
from subprocess import run, PIPE

from vang.bitbucket.get_repos import get_all_repos


def get_branch(git_dir):
    completed_process = run(shlex.split('git --git-dir {} rev-parse --abbrev-ref HEAD'.format(git_dir)),
                            universal_newlines=True, stdout=PIPE, stderr=PIPE)
    if completed_process.returncode:
        completed_process = run('git --git-dir {}/.git remote get-url origin'.format(git_dir).split(),
                                universal_newlines=True, stdout=PIPE)

    return completed_process.stdout.strip()


def get_clone_url(git_dir):
    completed_process = run(shlex.split('git --git-dir {} remote get-url origin'.format(git_dir)),
                            universal_newlines=True, stdout=PIPE, stderr=PIPE)
    if completed_process.returncode:
        completed_process = run('git --git-dir {}/.git remote get-url origin'.format(git_dir).split(),
                                universal_newlines=True, stdout=PIPE)

    return completed_process.stdout.strip()


def get_project_and_repo(git_dir):
    project, repo = get_clone_url(git_dir)[:-4].split('/')[-2:]
    return project.upper(), repo


def get_repo_specs(dirs, repos=None, projects=None):
    if projects:
        return get_all_repos(projects, only_spec=True, max_processes=10)
    elif repos:
        return (repo.split('/') for repo in repos)
    else:
        return (get_project_and_repo(dir) for dir in dirs)
