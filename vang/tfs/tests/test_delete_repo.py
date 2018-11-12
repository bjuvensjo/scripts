#!/usr/bin/env python3

from unittest.mock import call, patch

from pytest import raises

from vang.tfs.delete_repo import delete_repo, main, parse_args


def test_delete_repo():
    first_call_response = {'id': 'id'}
    second_call_response = 'response'
    with patch(
            'vang.tfs.delete_repo.call',
            side_effect=[first_call_response,
                         second_call_response]) as mock_call:
        assert second_call_response == delete_repo('org/project/name')
        assert [
            call(
                '/org/project/_apis/git/repositories/name?api-version=3.2',
                method='GET'),
            call(
                '/org/project/_apis/git/repositories/id?api-version=3.2',
                method='DELETE')
        ] == mock_call.mock_calls


def test_main():
    with patch(
            'vang.tfs.delete_repo.delete_repo',
            return_value='response') as mock_delete_repo:
        with patch('vang.tfs.delete_repo.print') as mock_print:
            main('repo')
            assert [call('repo')] == mock_delete_repo.mock_calls
            assert [call('response')] == mock_print.mock_calls


def test_parse_args():
    for args in ['', 'foo bar']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        [
            'organisation/project/repo',
            {
                'repo': 'organisation/project/repo'
            },
        ],
    ]:
        assert pargs == parse_args(args.split(' ')).__dict__
