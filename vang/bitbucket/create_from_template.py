#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.bitbucket.create_repo import create_repo
from vang.bitbucket.enable_webhooks import enable_repo_web_hook
from vang.bitbucket.get_clone_urls import get_clone_urls
from vang.bitbucket.set_default_branches import set_repo_default_branch
from vang.misc.s import get_zipped_cases
from vang.pio.rsr import _replace, rsr
from vang.pio.shell import run_command


def setup(project, repo, branch, dest_project, dest_repo, work_dir):
    clone_url = [c for _, p, r, c in get_clone_urls([project]) if r == repo][0]

    dest_repo_dir = f'{work_dir}/{dest_project}/{dest_repo}'
    run_command(f'git clone -b {branch} {clone_url} {dest_repo_dir}')

    run_command('rm -rf .git', return_output=True, cwd=dest_repo_dir)
    run_command('git init', return_output=True, cwd=dest_repo_dir)
    if not branch == 'master':
        run_command(
            f'git checkout -b {branch}', return_output=True, cwd=dest_repo_dir)
    return clone_url, dest_repo_dir


def commit_all(repo_dir):
    run_command('git add --all', return_output=True, cwd=repo_dir)
    run_command(
        'git commit -m "Initial commit"',
        return_output=True,
        cwd=repo_dir,
    )


def update(repo, dest_repo, dest_repo_dir):
    for old, new in get_zipped_cases([repo, dest_repo]):
        rsr(old, new, [dest_repo_dir], _replace(False))


def create_and_push_to_dest_repo(branch,
                                 dest_project,
                                 dest_repo,
                                 dest_repo_dir,
                                 webhook=None):
    dest_repo_origin = create_repo(dest_project,
                                   dest_repo)['links']['clone'][0]['href']
    if webhook:
        enable_repo_web_hook([dest_project, dest_repo], webhook)
    run_command(
        f'git remote add origin {dest_repo_origin}',
        return_output=True,
        cwd=dest_repo_dir)
    run_command(
        f'git push -u origin {branch}', return_output=True, cwd=dest_repo_dir)
    set_repo_default_branch((dest_project, dest_repo), branch)
    return dest_repo_origin


def main(project, repo, branch, dest_project, dest_repo, work_dir, webhook):
    clone_url, dest_repo_dir = setup(project, repo, branch, dest_project,
                                     dest_repo, work_dir)

    update(repo, dest_repo, dest_repo_dir)

    commit_all(dest_repo_dir)

    dest_repo_origin = create_and_push_to_dest_repo(
        branch, dest_project, dest_repo, dest_repo_dir, webhook)
    print('Created', dest_repo_origin)


def parse_args(args):
    parser = ArgumentParser(
        description='Create a new repo based on template'
        ' repo.\nExample: create_from_template.vang PCS1806 foo PCS1806'
        ' bar -b develop -d . -w http://my-host:7777/wildcat/webhook/')

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
        help='The branch to use and create, e.g. develop. '
        'It will be set as default branch on created repo')
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
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.src_project, args.src_repo, args.branch, args.dest_project,
         args.dest_repo, args.dir, args.webhook)
