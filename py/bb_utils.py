#!/usr/bin/env python3
import shlex
from subprocess import run, PIPE


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


def get_project_and_repo(clone_url):
    return clone_url.split('/')[-2].upper(), '.'.join(clone_url.split('/')[-1].split('.')[:-1])
