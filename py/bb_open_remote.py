#!/usr/bin/env python3
import shlex
import subprocess
from os.path import normpath
from re import sub

from bb_utils import get_clone_url, get_branch


def open_remote(git_dir):
    clone_url = get_clone_url(git_dir)
    branch = get_branch(git_dir)
    commits_url = sub(r'(.*)\/scm\/(.*)\/(.*).git',
                      r'\1/projects/\2/repos/\3/commits', clone_url)
    commits_branch_url = '{}?until=refs%2Fheads%2F{}&merges=include'.format(commits_url, branch)
    subprocess.run(shlex.split('open {}'.format(commits_branch_url)))


def main(repo_dir):
    open_remote(normpath('{}/.git'.format(repo_dir)))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Open origin url in browser.')
    parser.add_argument('-d', '--dir', default='.')
    args = parser.parse_args()

    main(args.dir)
