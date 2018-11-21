#!/usr/bin/env python3
from unittest.mock import call, patch
from pytest import raises
from re import match

from vang.git.filter_branch import create_random_name_and_email
from vang.git.filter_branch import filter_branch
from vang.git.filter_branch import get_emails
from vang.git.filter_branch import main
from vang.git.filter_branch import parse_args

import pytest


@pytest.mark.parametrize("clone_dir, committer, format", [
    ('clone_dir', False, '%ae'),
    ('clone_dir', True, '%ce'),
])
def test_get_emails(clone_dir, committer, format):
    with patch(
            'vang.git.filter_branch.run_command',
            return_value=(0, 'foo@myorg.com\n'
                          'foo@myorg.com\n'
                          'bar@myorg.com\n'
                          'foo@myorg.com')) as run_command:
        assert {'foo@myorg.com', 'bar@myorg.com'} == get_emails(
            clone_dir, committer)
        assert [
            call(f'git log --format="{format}"', True, clone_dir),
        ] == run_command.mock_calls


def test_filter_branch_no_old_email():
    with patch('vang.git.filter_branch.run_command') as run_command:
        filter_branch('clone_dir', 'new_name', 'new_email')
        assert [
            call(
                '''git filter-branch --force --env-filter '
        export GIT_COMMITTER_NAME="new_name"
        export GIT_COMMITTER_EMAIL="new_email"
        export GIT_AUTHOR_NAME="new_name"
        export GIT_AUTHOR_EMAIL="new_email"
    ' --tag-name-filter cat -- --branches --tags
    ''', True, 'clone_dir')
        ] == run_command.mock_calls


def test_filter_branch_old_email():
    with patch('vang.git.filter_branch.run_command') as run_command:
        filter_branch('clone_dir', 'new_name', 'new_email', 'old_email')
        assert [
            call(
                '''git filter-branch --force --env-filter '
        if [ "$GIT_COMMITTER_EMAIL" = "old_email" ]
        then
            export GIT_COMMITTER_NAME="new_name"
            export GIT_COMMITTER_EMAIL="new_email"
        fi
        if [ "$GIT_AUTHOR_EMAIL" = "old_email" ]
        then
            export GIT_AUTHOR_NAME="new_name"
            export GIT_AUTHOR_EMAIL="new_email"
        fi
    ' --tag-name-filter cat -- --branches --tags
    ''', True, 'clone_dir')
        ] == run_command.mock_calls


def test_create_random_name_and_email():
    name, email = create_random_name_and_email()
    assert name == email.split('@')[0]
    assert match(r'dev.[0-9]{7}@it.com', email)


@patch('vang.git.filter_branch.filter_branch')
@patch('vang.git.filter_branch.print')
@patch(
    'vang.git.filter_branch.create_random_name_and_email',
    return_value=('random', 'random@bar.com'))
@patch('vang.git.filter_branch.get_emails', return_value={'foo@bar.com'})
def test_main_not_distinct(mock_get_emails, mock_create_random_name_and_email,
                           mock_print, mock_filter_branch):
    main('clone_dir', False)
    assert [call('clone_dir'), call('clone_dir',
                                    True)] == mock_get_emails.mock_calls
    assert [call()] == mock_create_random_name_and_email.mock_calls
    assert [
        call('Filtering: * -> random@bar.com'),
        call('########################################'
             '########################################'),
        call('emails after filtering:', "{'foo@bar.com'}")
    ] == mock_print.mock_calls
    assert [call(
        'clone_dir',
        'random',
        'random@bar.com',
    )] == mock_filter_branch.mock_calls


@patch('vang.git.filter_branch.filter_branch')
@patch('vang.git.filter_branch.print')
@patch(
    'vang.git.filter_branch.create_random_name_and_email',
    return_value=('random', 'random@bar.com'))
@patch(
    'vang.git.filter_branch.get_emails',
    return_value={'foo@bar.com', 'baz@bar.com'})
def test_main_distinct(mock_get_emails, mock_create_random_name_and_email,
                       mock_print, mock_filter_branch):
    main('clone_dir', True)
    assert [
        call('clone_dir'),
        call('clone_dir', True),
        call('clone_dir'),
        call('clone_dir', True),
    ] == mock_get_emails.mock_calls

    assert [
        call(),
        call(),
    ] == mock_create_random_name_and_email.mock_calls

    mock_print.has_calls([
        call('Filtering: foo@bar.com -> random@bar.com'),
        call('Filtering: baz@bar.com -> random@bar.com'),
        call('########################################'
             '########################################'),
        call('emails after filtering:', "{'foo@bar.com', 'baz@bar.com'}")
    ])

    mock_filter_branch.assert_has_calls([
        call('clone_dir', 'random', 'random@bar.com', 'baz@bar.com'),
        call('clone_dir', 'random', 'random@bar.com', 'foo@bar.com')
    ],
                                        any_order=True)


@pytest.mark.parametrize("args", [
    '-e e',
    'foo',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['', {
        'clone_dir': '.',
        'distinct': False
    }],
    ['-c clone_dir -d', {
        'clone_dir': 'clone_dir',
        'distinct': True
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
