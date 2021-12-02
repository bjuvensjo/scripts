#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv

from vang.misc.s import get_zipped_cases
from vang.pio.rsr import get_replace_function, rsr
from vang.pio.shell import run_command
from vang.tfs.clone_repos import clone_repos
from vang.tfs.create_repo import create_repo


def setup(repo, src_branch,  dest_repo, dest_branch, work_dir):
    clone_url, repo_dir = clone_repos(
        work_dir,
        repos=[repo],
        branch=src_branch,
    )[0]

    dest_repo_dir = f'{work_dir}/{dest_repo}'
    run_command(f'mv {repo_dir} {dest_repo_dir}')

    run_command('rm -rf .git', return_output=True, cwd=dest_repo_dir)
    run_command('git init', return_output=True, cwd=dest_repo_dir)
    if not dest_branch == 'master':
        run_command(
            f'git checkout -b {dest_branch}',
            return_output=True,
            cwd=dest_repo_dir,
        )
    return clone_url, dest_repo_dir


def commit_all(repo_dir):
    run_command('git add --all', return_output=True, cwd=repo_dir)
    run_command(
        'git commit -m "Initial commit"',
        return_output=True,
        cwd=repo_dir,
    )


def update(replacements, dest_repo_dir):
    for pair in replacements:
        for old, new in set(get_zipped_cases(pair)):
            rsr(
                old,
                new,
                [dest_repo_dir],
                get_replace_function(False),
            )


def create_and_push_to_dest_repo(
        branch,
        dest_repo,
        dest_repo_dir,
):
    dest_repo_origin = create_repo(dest_repo)['remoteUrl']
    run_command(
        f'git remote add origin {dest_repo_origin}',
        return_output=True,
        cwd=dest_repo_dir)
    run_command(
        f'git push -u origin {branch}',
        return_output=True,
        cwd=dest_repo_dir,
    )
    return dest_repo_origin


def parse_args(args):
    parser = ArgumentParser(
        description='Create a new repo based on template'
                    ' repo.\nExample: create_from_template PCS1906/foo PCS1906/bar'
                    ' -sb sourcebranch -db destinationbranch -d .')
    parser.add_argument(
        'src_repo',
        help='The repo from which to create the new repo (must exist)'
             ', e.g. organisation/project/repo1',
    )
    parser.add_argument(
        'dest_repo',
        help='The new repo (must not exist), '
             'e.g. organisation/project/repo2',
    )
    parser.add_argument(
        '-sb',
        '--src_branch',
        default='develop',
        help='The branch to use, e.g. develop',
    )
    parser.add_argument(
        '-db',
        '--dest_branch',
        default='develop',
        help='The branch to create, e.g. develop. '
             'It will be set as default branch on created repo',
    )
    parser.add_argument(
        '-d',
        '--work_dir',
        default='.',
        help='The directory to create local repo in',
    )
    parser.add_argument(
        '-r',
        '--replacements',
        default=[],
        nargs='+',
        help='Pairs of replacements, e.i. the first in the pair is a string in the src_repo that will be replaced to the second in the pair in the dest_repo',
    )
    return parser.parse_args(args)


def main(
        src_repo,
        src_branch,
        dest_repo,
        dest_branch,
        work_dir,
        replacements,
):
    if len(replacements) % 2 > 0:
        print("Error: Replacements must be pairs")
        exit(1)

    clone_url, dest_repo_dir = setup(
        src_repo,
        src_branch,
        dest_repo,
        dest_branch,
        work_dir,
    )

    replacement_pairs = list(zip(replacements[0::2], replacements[1::2]))
    update(replacement_pairs, dest_repo_dir)

    commit_all(dest_repo_dir)

    dest_repo_origin = create_and_push_to_dest_repo(
        dest_branch,
        dest_repo,
        dest_repo_dir,
    )
    print('Created', dest_repo_origin)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
