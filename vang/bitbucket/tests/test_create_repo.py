#!/usr/bin/env python3

from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.create_repo import create_repo
from vang.bitbucket.create_repo import main
from vang.bitbucket.create_repo import parse_args


@patch('vang.bitbucket.create_repo.call')
def test_create_repo(mock_call):
    create_repo('project', 'repo')
    assert [
               call('/rest/api/1.0/projects/project/repos',
                    {"name": "repo", "scmId": "git", "forkable": True}, 'POST')
           ] == mock_call.mock_calls


@patch(
    'vang.bitbucket.create_repo.create_repo',
    return_value={'links': {
        'clone': [{
            'href': 'clone_url'
        }]
    }})
@patch('builtins.print')
def test_main(mock_print, mock_create_repo):
    assert not main('project', 'repo')
    with patch('vang.bitbucket.create_repo.name', 'posix'):
        assert [
                   call('If you already have code ready to be pushed to this '
                        'repository then run this in your terminal.'),
                   call('    git remote add origin clone_url\n'
                        '    git push -u origin develop'),
                   call('(The commands are copied to the clipboard)')
               ] == mock_print.mock_calls
    mock_print.reset_mock()
    with patch('vang.bitbucket.create_repo.name', 'not-posix'):
        main('project', 'repo')
        assert [
                   call('If you already have code ready to be pushed to this '
                        'repository then run this in your terminal.'),
                   call('    git remote add origin clone_url\n'
                        '    git push -u origin develop')
               ] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    'foo bar baz',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['project repo', {
        'project': 'project',
        'repository': 'repo'
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
