#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.get_clone_urls_grep import get_clone_urls_grep
from vang.bitbucket.get_clone_urls_grep import main
from vang.bitbucket.get_clone_urls_grep import parse_args

import pytest


@pytest.fixture
def projects_fixture():
    return [{
        'key': f'P{n}',
        'id': 1250,
        'name': f'P{n}',
        'public': False,
        'type': 'NORMAL',
        'links': {
            'self': [{
                'href': f'http://myorg/stash/projects/p{n}'
            }]
        }
    } for n in range(25)]


@pytest.fixture
def clone_urls_fixture():
    return [(None, 'Px', 'repo_slug',
             'http://myorgn/stash/scm/px/repo_slug.git')]


@patch('vang.bitbucket.get_clone_urls_grep.get_clone_urls', autospec=True)
@patch('vang.bitbucket.get_clone_urls_grep.get_projects', autospec=True)
def test_get_clone_urls_grep(
        mock_get_projects,
        mock_get_clone_urls,
        projects_fixture,
        clone_urls_fixture,
):
    mock_get_projects.return_value = projects_fixture
    mock_get_clone_urls.return_value = clone_urls_fixture
    assert clone_urls_fixture == get_clone_urls_grep(['.*4', 'P2.*'])
    assert [call()] == mock_get_projects.mock_calls
    assert [
        call(['P2', 'P4', 'P14', 'P20', 'P21', 'P22', 'P23', 'P24'], False)
    ] == mock_get_clone_urls.mock_calls


@patch('vang.bitbucket.get_clone_urls_grep.print')
@patch('vang.bitbucket.get_clone_urls_grep.get_clone_urls_grep', autospec=True)
def test_main(mock_get_clone_urls_grep, mock_print, clone_urls_fixture):
    mock_get_clone_urls_grep.return_value = clone_urls_fixture
    main(['.*'], False)
    assert [call('http://myorgn/stash/scm/px/repo_slug.git')
            ] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else '')


@pytest.mark.parametrize("args, expected", [
    ['p1 p2', {
        'patterns': ['p1', 'p2'],
        'command': False,
    }],
    ['p1 p2 -c', {
        'patterns': ['p1', 'p2'],
        'command': True,
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
