#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.get_branches import get_all_branches
from vang.bitbucket.get_branches import get_branch_page
from vang.bitbucket.get_branches import get_branches
from vang.bitbucket.get_branches import main
from vang.bitbucket.get_branches import parse_args

import pytest


@pytest.fixture
def call_fixtures():
    return [
        {
            'size':
            25,
            'limit':
            25,
            'isLastPage':
            False,
            'values':
            [{
                'id': 'refs/heads/develop',
                'displayId': 'develop',
                'type': 'BRANCH',
                'latestCommit': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                'latestChangeset': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                'isDefault': True
            }] * 25,
            'start':
            0
        },
        {
            'size':
            25,
            'limit':
            25,
            'isLastPage':
            True,
            'values':
            [{
                'id': 'refs/heads/develop',
                'displayId': 'develop',
                'type': 'BRANCH',
                'latestCommit': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                'latestChangeset': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                'isDefault': True
            }] * 25,
            'start':
            0
        },
    ]


@patch('vang.bitbucket.get_branches.call')
def test_get_branch_page(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures[0]
    assert (
        call_fixtures[0]['size'],
        call_fixtures[0]['values'],
        call_fixtures[0]['isLastPage'],
        call_fixtures[0].get('nextPageStart', -1),
    ) == get_branch_page(['project_key', 'repo_slug'], 'develop', 25, 0)
    assert [
        call('/rest/api/1.0/projects/project_key/repos/'
             'repo_slug/branches?filterText=develop&limit=25&start=0')
    ] == mock_call.mock_calls


@patch('vang.bitbucket.get_branches.call')
def test_get_all_branches(mock_call, call_fixtures):
    mock_call.side_effect = call_fixtures
    assert (['project_key', 'repo_slug'], call_fixtures[0]['values'] +
            call_fixtures[1]['values']) == get_all_branches(
                ['project_key', 'repo_slug'], 'branch')


@pytest.fixture
def branches_fixture():
    return (('project_key', 'repo_slug'),
            [{
                'id': 'refs/heads/release',
                'displayId': 'release',
                'type': 'BRANCH',
                'latestCommit': 'f89ed59695b89280c474d6c20f6c026dee7eca06',
                'latestChangeset': 'f89ed59695b89280c474d6c20f6c026dee7eca06',
                'isDefault': False
            },
             {
                 'id': 'refs/heads/develop',
                 'displayId': 'develop',
                 'type': 'BRANCH',
                 'latestCommit': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                 'latestChangeset': 'c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767',
                 'isDefault': True
             }])


@patch('vang.bitbucket.get_branches.get_all_branches')
def test_get_branches(mock_get_all_branches, branches_fixture):
    mock_get_all_branches.return_value = branches_fixture
    assert [branches_fixture] * 2 == list(
        get_branches([
            ['project_key', 'repo_slug'],
            ['project_key', 'repo_slug'],
        ], ''))


@pytest.mark.parametrize("name, print_calls", [
    (True, [
        call('release'),
        call('develop'),
    ]),
    (False, [
        call('project_key/repo_slug: release'),
        call('project_key/repo_slug: develop'),
    ]),
])
@patch('vang.bitbucket.get_branches.print')
@patch('vang.bitbucket.get_branches.get_branches')
@patch('vang.bitbucket.get_branches.get_repo_specs')
def test_main(
        mock_get_repo_specs,
        mock_get_branches,
        mock_print,
        name,
        print_calls,
        branches_fixture,
):
    mock_get_repo_specs.return_value = [['project_key', 'repo_slug']]
    mock_get_branches.return_value = [branches_fixture]
    main(name=name, dirs=['.'])
    assert [call(['.'], None, None)] == mock_get_repo_specs.mock_calls
    assert [call([['project_key', 'repo_slug']],
                 '')] == mock_get_branches.mock_calls
    assert print_calls == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '-d d -r r',
    '-d d -p p',
    '-r r -p p',
    '1',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        '',
        {
            'branch': '',
            'dirs': ['.'],
            'name': False,
            'projects': None,
            'repos': None,
        }
    ],
    [
        '-b b -n -d d1 d2',
        {
            'branch': 'b',
            'dirs': ['d1', 'd2'],
            'name': True,
            'projects': None,
            'repos': None
        }
    ],
    [
        '-b b -n -r p/r1 p/r2',
        {
            'branch': 'b',
            'dirs': ['.'],
            'name': True,
            'projects': None,
            'repos': ['p/r1', 'p/r2']
        }
    ],
    [
        '-b b -n -p p1 p2',
        {
            'branch': 'b',
            'dirs': ['.'],
            'name': True,
            'projects': ['p1', 'p2'],
            'repos': None
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
