#!/usr/bin/env python3
from argparse import ArgumentParser
from random import randint
from sys import argv

from vang.pio.shell import run_command


def get_emails(clone_dir, committer=False):
    log_format = '%ce' if committer else '%ae'
    rc, output = run_command(
        f'git log --format="{log_format}"',
        True,
        clone_dir,
    )
    return set(output.split('\n'))


def filter_branch(clone_dir, new_name, new_email, old_email=None):
    filter_branch_command = f'''git filter-branch --force --env-filter '
        if [ "$GIT_COMMITTER_EMAIL" = "{old_email}" ]
        then
            export GIT_COMMITTER_NAME="{new_name}"
            export GIT_COMMITTER_EMAIL="{new_email}"
        fi
        if [ "$GIT_AUTHOR_EMAIL" = "{old_email}" ]
        then
            export GIT_AUTHOR_NAME="{new_name}"
            export GIT_AUTHOR_EMAIL="{new_email}"
        fi
    ' --tag-name-filter cat -- --branches --tags
    ''' if old_email else f'''git filter-branch --force --env-filter '
        export GIT_COMMITTER_NAME="{new_name}"
        export GIT_COMMITTER_EMAIL="{new_email}"
        export GIT_AUTHOR_NAME="{new_name}"
        export GIT_AUTHOR_EMAIL="{new_email}"
    ' --tag-name-filter cat -- --branches --tags
    '''
    return run_command(filter_branch_command, True, clone_dir)


def create_random_name_and_email():
    name = f'dev.{randint(1000000, 9999999)}'
    return name, f'{name}@it.com'


def main(clone_dir, distinct=False):
    if distinct:
        for email in set(get_emails(clone_dir) | get_emails(clone_dir, True)):
            new_name, new_email = create_random_name_and_email()
            print(f'Filtering: {email} -> {new_email}')
            filter_branch(clone_dir, new_name, new_email, email)
    else:
        new_name, new_email = create_random_name_and_email()
        print(f'Filtering: * -> {new_email}')
        filter_branch(clone_dir, new_name, new_email)

    print('#' * 80)
    print(
        'emails after filtering:',
        f'{set(get_emails(clone_dir) | get_emails(clone_dir, True))}',
    )


def parse_args(args):
    parser = ArgumentParser(
        description='Randomize author and commit names for all git commits.')
    parser.add_argument(
        '-c', '--clone_dir', help='The git repo directory', default='.')
    parser.add_argument(
        '-d', '--distinct', help='If distinct mapping', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    sure = input("Sure? (y/n): ") == 'y'
    if sure:
        main(**parse_args(argv[1:]).__dict__)
