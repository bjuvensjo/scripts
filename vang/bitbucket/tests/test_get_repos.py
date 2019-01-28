#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.get_repos import get_all_repos
from vang.bitbucket.get_repos import get_repos
from vang.bitbucket.get_repos import get_repos_page
from vang.bitbucket.get_repos import main
from vang.bitbucket.get_repos import parse_args

import pytest


def get_call_fixtures(start, end, last):
    response = {
        'size':
        end - start,
        'limit':
        end - start,
        'isLastPage':
        last,
        'values': [{
            'slug': f'r{n}',
            'id': 9000 + n,
            'name': f'r{n}',
            'scmId': 'git',
            'state': 'AVAILABLE',
            'statusMessage': 'Available',
            'forkable': True,
            'project': {
                'key': 'project_key',
                'id': 1000 + n,
                'name': 'project_name',
                'public': False,
                'type': 'NORMAL',
                'links': {
                    'self': [{
                        'href': 'http://myorg/stash/projects/project_key'
                    }]
                }
            },
            'public': False,
            'links': {
                'clone': [{
                    'href':
                    f'http://myorg/stash/scm/project_key/r{n}.git',
                    'name':
                    'http'
                }],
                'self': [{
                    'href':
                    f'http://myorg/stash/projects/project_key/repos/r{n}/browse'
                }]
            }
        } for n in range(start, end)],
        'start':
        start
    }
    return response if last else dict(response, nextPageStart=end)


def get_the_call_fixtures():
    return [get_call_fixtures(0, 25, False), get_call_fixtures(25, 30, True)]


@pytest.fixture
def call_fixtures():
    return get_the_call_fixtures()


@patch('vang.bitbucket.get_repos.call', autospec=True)
def test_get_repos_page(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures[0]
    assert (
        call_fixtures[0]['size'],
        call_fixtures[0]['values'],
        call_fixtures[0]['isLastPage'],
        call_fixtures[0].get('nextPageStart', -1),
    ) == get_repos_page('project_key', call_fixtures[0]['limit'],
                        call_fixtures[0]['start'])
    assert [call('/rest/api/1.0/projects/project_key/repos?limit=25&start=0')
            ] == mock_call.mock_calls


@pytest.mark.parametrize("only_name, only_spec, expected", [
    (False, False, [v for r in get_the_call_fixtures() for v in r['values']]),
    (True, False, [f'r{n}' for n in range(30)]),
    (False, True, [('project_key', f'r{n}') for n in range(30)]),
])
@patch('vang.bitbucket.get_repos.call', autospec=True)
def test_get_repos(mock_call, only_name, only_spec, expected, call_fixtures):
    mock_call.side_effect = call_fixtures
    assert expected == list(get_repos('project_key', only_name, only_spec))


@patch('vang.bitbucket.get_repos.get_repos', autospec=True)
def test_get_all_repos(mock_get_repos):
    mock_get_repos.return_value = ['r']
    assert ['r', 'r'] == list(get_all_repos(['p1', 'p2']))
    assert [
        call('p1', False, False),
        call('p2', False, False),
    ] == mock_get_repos.mock_calls


@pytest.mark.parametrize("only_name, only_spec, expected", [
    (False, False,
     [call(v) for r in get_the_call_fixtures() for v in r['values']]),
    (True, False, [call(f'r{n}') for n in range(30)]),
    (False, True, [call(f'project_key/r{n}') for n in range(30)]),
])
@patch('vang.bitbucket.get_repos.print')
@patch('vang.bitbucket.get_repos.call', autospec=True)
def test_main(mock_call, mock_print, only_name, only_spec, expected,
              call_fixtures):
    mock_call.side_effect = call_fixtures
    main(['project_key'], only_name, only_spec)
    assert expected == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '-n',
    '-r',
    '1 -n -r',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else '')


@pytest.mark.parametrize("args, expected", [
    ['p1 p2', {
        'projects': ['p1', 'p2'],
        'name': False,
        'repo_specs': False,
    }],
    [
        'p1 p2 -n',
        {
            'projects': ['p1', 'p2'],
            'name': True,
            'repo_specs': False,
        }
    ],
    [
        'p1 p2 -r',
        {
            'projects': ['p1', 'p2'],
            'name': False,
            'repo_specs': True,
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
