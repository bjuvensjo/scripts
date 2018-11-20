#!/usr/bin/env python3

from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.get_branches import get_branches, get_repo_branches, main, parse_args


def test_get_repo_branches():
    with patch(
            'vang.tfs.get_branches.call',
            return_value={
                'value': [{
                    'name':
                    'refs/heads/develop',
                    'objectId':
                    '071bd4a8b19c37b2c5290b127c787f8acd52272e',
                    'url':
                    'remoteUrl',
                    'statuses': []
                }],
                'count':
                1
            },
            autospec=True) as mock_call:
        assert [{
            'name': 'refs/heads/develop',
            'objectId': '071bd4a8b19c37b2c5290b127c787f8acd52272e',
            'url': 'remoteUrl',
            'statuses': []
        }] == get_repo_branches('organisation', 'project', 'repository')
        assert [
            call('/organisation/project/_apis/git/'
                 'repositories/repository/refs/heads?includeStatuses=true'
                 '&api-version=3.2')
        ] == mock_call.mock_calls


def test_get_branches():
    assert [] == get_branches(None)
    assert [] == get_branches([])
    with patch(
            'vang.tfs.get_branches.get_repos',
            return_value=['organisation/project/repo'],
            autospec=True) as mock_get_repos:
        with patch(
                'vang.tfs.get_branches.get_repo_branches',
                return_value=[{
                    'name':
                    'refs/heads/develop',
                    'objectId':
                    '071bd4a8b19c37b2c5290b127c787f8acd52272e',
                    'url':
                    'remoteUrl',
                    'statuses': []
                }],
                autospec=True) as mock_get_repo_branches:
            assert [('organisation/project/repo', [{
                'name':
                'develop',
                'objectId':
                '071bd4a8b19c37b2c5290b127c787f8acd52272e',
                'statuses': [],
                'url':
                'remoteUrl'
            }])] == get_branches(organisations=['organisation'])
            assert [call(organisations=['organisation'],
                         repo_specs=True)] == mock_get_repos.mock_calls
            assert [call('organisation', 'project',
                         'repo')] == mock_get_repo_branches.mock_calls
            mock_get_repos.reset_mock()
            mock_get_repo_branches.reset_mock()

            assert [('organisation/project/repo', [{
                'name':
                'develop',
                'objectId':
                '071bd4a8b19c37b2c5290b127c787f8acd52272e',
                'statuses': [],
                'url':
                'remoteUrl'
            }])] == get_branches(projects=['organisation/project'])
            assert [call(projects=['organisation/project'],
                         repo_specs=True)] == mock_get_repos.mock_calls
            assert [call('organisation', 'project',
                         'repo')] == mock_get_repo_branches.mock_calls
            mock_get_repos.reset_mock()
            mock_get_repo_branches.reset_mock()

            assert [('organisation/project/repo', [{
                'name':
                'develop',
                'objectId':
                '071bd4a8b19c37b2c5290b127c787f8acd52272e',
                'statuses': [],
                'url':
                'remoteUrl'
            }])] == get_branches(repos=['organisation/project/repo'])
            assert [] == mock_get_repos.mock_calls
            assert [call('organisation', 'project',
                         'repo')] == mock_get_repo_branches.mock_calls

            assert [
                ('organisation/project/repo', ['develop']),
            ] == get_branches(
                repos=['organisation/project/repo'], names=True)


@pytest.mark.parametrize("args", [
    '',
    '-o o -p -p',
    '-o o -r -r',
    '-p -p -r r',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        '-o o1 o2',
        {
            'names': False,
            'organisations': ['o1', 'o2'],
            'projects': None,
            'repos': None
        }
    ],
    [
        '-p p1 p2',
        {
            'names': False,
            'organisations': None,
            'projects': ['p1', 'p2'],
            'repos': None
        }
    ],
    [
        '-r r1 r2',
        {
            'names': False,
            'organisations': None,
            'projects': None,
            'repos': ['r1', 'r2']
        }
    ],
    [
        '-o o -n',
        {
            'names': True,
            'organisations': ['o'],
            'projects': None,
            'repos': None
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__


def test_main():
    with patch(
            'vang.tfs.get_branches.get_branches',
            return_value=[['r1', ['b1', 'b2']], ['r2', ['b1', 'b2']]],
            autospec=True,
    ) as mock_get_branches:
        with patch('vang.tfs.get_branches.print') as mock_print:
            main('organisations', None, None, False)
            assert [call('organisations', None, None,
                         False)] == mock_get_branches.mock_calls
            assert [
                call('r1: b1'),
                call('r1: b2'),
                call('r2: b1'),
                call('r2: b2')
            ] == mock_print.mock_calls
