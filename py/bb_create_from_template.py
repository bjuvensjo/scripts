#!/usr/bin/env python3

import sys
from functools import partial
from multiprocessing.dummy import Pool
from traceback import print_exc

# import bb_fork_repo_git_shallow
import bb_create_repo
import bb_enable_webhooks
import bb_get_clone_urls
import bb_set_default_branches
import rsr
import s
import shell


def setup(project, repo, branch, dest_project, dest_repo, work_dir):
    clone_url = [
        c for _, p, r, c in bb_get_clone_urls.get_clone_urls([project])
        if r == repo
    ][0]

    dest_repo_dir = '{}/{}/{}'.format(work_dir, dest_project, dest_repo)
    shell.run_command('git clone {} {}'.format(clone_url, dest_repo_dir))

    shell.run_command('rm -rf .git', return_output=True, cwd=dest_repo_dir)
    shell.run_command('git init', return_output=True, cwd=dest_repo_dir)
    if not branch == 'master':
        shell.run_command(
            'git checkout -b ' + branch, return_output=True, cwd=dest_repo_dir)
    return clone_url, dest_repo_dir


def commit_all(repo_dir):
    shell.run_command('git add --all', return_output=True, cwd=repo_dir)
    shell.run_command(
        'git commit -m "Initial commit"',
        return_output=True,
        cwd=repo_dir,
    )


def update(repo, dest_repo, dest_repo_dir):
    for old, new in s.get_zipped_cases([repo, dest_repo]):
        rsr.rsr(old, new, [dest_repo_dir], rsr._replace(False))


def create_and_push_to_dest_repo(branch,
                                 dest_project,
                                 dest_repo,
                                 dest_repo_dir,
                                 webhook=None):
    dest_repo_origin = bb_create_repo.create_repo(
        dest_project, dest_repo)['links']['clone'][0]['href']
    if webhook:
        bb_enable_webhooks.enable_repo_web_hook([dest_project, dest_repo],
                                                webhook)
    shell.run_command(
        'git remote add origin {}'.format(dest_repo_origin),
        return_output=True,
        cwd=dest_repo_dir)
    shell.run_command(
        'git push -u origin {}'.format(branch),
        return_output=True,
        cwd=dest_repo_dir)
    bb_set_default_branches.set_repo_default_branch((dest_project, dest_repo),
                                                    branch)
    return dest_repo_origin


def main(project, repo, branch, dest_project, dest_repo, work_dir, webhook):
    clone_url, dest_repo_dir = setup(project, repo, branch, dest_project,
                                     dest_repo, work_dir)

    update(repo, dest_repo, dest_repo_dir)

    commit_all(dest_repo_dir)

    dest_repo_origin = create_and_push_to_dest_repo(
        branch, dest_project, dest_repo, dest_repo_dir, webhook)
    print('Created', dest_repo_origin)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='''
       Create a new repo based on template repo.
       Example: bb_create_from_template.py PCS1806 foo PCS1806 bar -b develop -d . -w http://my-host:7777/wildcat/webhook/
    ''')
    parser.add_argument(
        'src_project',
        help='The project from which to create the new repo (must exist)')
    parser.add_argument(
        'src_repo',
        help='The repo from which to create the new repo (must exist)')
    parser.add_argument(
        'dest_project',
        help='The project in which to create the new repo (must not exist)')
    parser.add_argument('dest_repo', help='The new repo (must not exist)')
    parser.add_argument(
        '-b',
        '--branch',
        default='develop',
        help=
        'The branch to use and create, e.g. develop. It will be set as default branch on created repo'
    )
    parser.add_argument(
        '-d',
        '--dir',
        default='.',
        help='The directory to create local repo in')
    parser.add_argument(
        '-w',
        '--webhook',
        default=False,
        help='Webhook url to add to the new repo')

    args = parser.parse_args()

    main(args.src_project, args.src_repo, args.branch, args.dest_project,
         args.dest_repo, args.dir, args.webhook)
