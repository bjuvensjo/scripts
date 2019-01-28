#!/usr/bin/env python3

from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.create_repo import create_repo, main, parse_args


def test_create_repo():
    call_response = 'response'
    with patch(
            'vang.tfs.create_repo.call', return_value=call_response,
            autospec=True) as mock_call:
        assert call_response == create_repo('organisation/project/name')
        assert [
            call(
                '/organisation/project/_apis/git/repositories?api-version=3.2',
                method='POST',
                request_data={'name': 'name'})
        ] == mock_call.mock_calls


def test_main():
    with patch(
            'vang.tfs.create_repo.create_repo',
            return_value={'remoteUrl': 'remoteUrl'},
            autospec=True):
        with patch('vang.tfs.create_repo.print') as mock_print:
            with patch('vang.tfs.create_repo.os_name', 'not_posix'):
                main('organisation/project/repo')
                assert [
                    call('If you already have code ready to be pushed to this '
                         'repository then run this in your terminal.'),
                    call('    git remote add origin remoteUrl\n'
                         '    git push -u origin develop')
                ] == mock_print.mock_calls
        with patch('vang.tfs.create_repo.print') as mock_print:
            with patch('vang.tfs.create_repo.os_name', 'posix'):
                with patch(
                        'vang.tfs.create_repo.system',
                        autospec=True) as mock_system:
                    main('organisation/project/repo')
                    assert [
                        call('If you already have code ready to be pushed to '
                             'this repository then run this in your terminal.'),
                        call('    git remote add origin remoteUrl\n'
                             '    git push -u origin develop'),
                        call('(The commands are copied to the clipboard)')
                    ] == mock_print.mock_calls
                    assert [
                        call('echo "    git remote add origin remoteUrl\n'
                             '    git push -u origin develop\\c" | pbcopy')
                    ] == mock_system.mock_calls


@pytest.mark.parametrize("args", ['', 'foo bar'])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['organisation/project/repo', {
        'repo': 'organisation/project/repo'
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__
