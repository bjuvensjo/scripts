#!/usr/bin/env python3
import argparse
import sys
from functools import partial
from multiprocessing.dummy import Pool
from traceback import print_exc

import vang.bitbucket.clone_repos as clone_repos
from vang.bitbucket.create_repo import create_repo
from vang.bitbucket.set_default_branches import set_repo_default_branch
from vang.pio.command_all import get_work_dirs
from vang.pio.shell import run_command


def fork_repo(fork_project, branches, git_dir):
    try:
        for b in reversed(branches):
            run_command(f'git checkout {b}', return_output=True, cwd=git_dir)
        rc, original_origin = run_command(
            'git remote get-url origin', return_output=True, cwd=git_dir)
        repo = original_origin.split('/')[-1][:-4]
        new_origin = '/'.join(original_origin.split(
            '/')[:-2]) + '/' + fork_project.lower() + '/' + repo + '.git'
        create_repo(fork_project, repo)
        run_command(
            f'git remote set-url origin {new_origin}',
            return_output=True,
            cwd=git_dir)
        run_command('git remote prune origin', return_output=True, cwd=git_dir)
        for b in branches:
            run_command(
                f'git push -u origin {b}', return_output=True, cwd=git_dir)
        set_repo_default_branch((fork_project, repo), branches[0])

        print(f'{fork_project}/{repo}: {new_origin}')
        return (fork_project, repo), new_origin
    except OSError:  # pragma: no cover
        print(f'Error forking {git_dir}')
        print_exc(file=sys.stdout)


def fork_repos(fork_project,
               branches,
               work_dir='.',
               repos=None,
               projects=None,
               max_processes=10):
    clone_repos.main(work_dir, projects, repos, branch=branches[0], flat=True)
    git_dirs = get_work_dirs('.git/', work_dir)
    with Pool(processes=max_processes) as pool:
        pool.map(partial(fork_repo, fork_project, branches), git_dirs)


def main(fork_project, branches, work_dir='.', repos=None, projects=None):
    fork_repos(fork_project, branches, work_dir, repos, projects)


def parse_args(args):
    parser = argparse.ArgumentParser(description='''
       Fork Bitbucket repos by cloning repos,
       create new repos in fork project,
       set them as origin
       and push branches to new repos
    ''')
    parser.add_argument('fork_project', help='Fork project (must exist)')
    parser.add_argument(
        '-b',
        '--branches',
        nargs='*',
        help='The branches to fork, e.g. develop master. '
        'The first will be set as default branch',
        default=['develop'])
    parser.add_argument(
        '-d', '--work_dir', default='.', help='The directory to clone into. Preferably an empty directory!')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument(
        '-p', '--projects', nargs='*', help='Projects, e.g. key1 key2')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(sys.argv[1:]).__dict__)
