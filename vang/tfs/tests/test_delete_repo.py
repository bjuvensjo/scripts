#!/usr/bin/env python3

from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.delete_repo import delete_repo, main, parse_args


def test_delete_repo():
    first_call_response = {'id': 'id'}
    second_call_response = 'response'
    with patch(
            'vang.tfs.delete_repo.call',
            side_effect=[first_call_response, second_call_response],
            autospec=True) as mock_call:
        assert second_call_response == delete_repo('org/project/name')
        assert [
            call(
                '/org/project/_apis/git/repositories/name?api-version=3.2',
                method='GET'),
            call(
                '/org/project/_apis/git/repositories/id?api-version=3.2',
                method='DELETE', only_response_code=True)
        ] == mock_call.mock_calls


def test_main():
    with patch(
            'vang.tfs.delete_repo.delete_repo',
            return_value='response',
            autospec=True) as mock_delete_repo:
        with patch('vang.tfs.delete_repo.print') as mock_print:
            main('repo')
            assert [call('repo')] == mock_delete_repo.mock_calls
            assert [call('response')] == mock_print.mock_calls


@pytest.mark.parametrize("args", ['', 'foo bar'])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        'organisation/project/repo',
        {
            'repo': 'organisation/project/repo'
        },
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__
