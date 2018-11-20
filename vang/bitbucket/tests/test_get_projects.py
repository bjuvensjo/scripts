#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.get_projects import get_projects_page
from vang.bitbucket.get_projects import get_projects
from vang.bitbucket.get_projects import main
from vang.bitbucket.get_projects import parse_args

import pytest


@pytest.mark.parametrize("call_response, expected", [
    ({
        'size': 1,
        'values': ['v1'],
        'isLastPage': True,
    }, (
        1,
        ['v1'],
        True,
        -1,
    )),
    ({
        'size': 1,
        'values': ['v1'],
        'isLastPage': False,
        'nextPageStart': 2
    }, (
        1,
        ['v1'],
        False,
        2,
    )),
])
def test_get_projects_page(call_response, expected):
    with patch('vang.bitbucket.get_projects.call') as mock_call:
        mock_call.return_value = call_response
        assert expected == get_projects_page(10, 0)
        assert [call('/rest/api/1.0/projects?limit=10&start=0')
                ] == mock_call.mock_calls


@pytest.fixture
def projects():
    return [{'key': f'k{n}', 'name': f'n{n}'} for n in range(50)]


@patch('vang.bitbucket.get_projects.get_projects_page')
def test_get_projects(mock_get_projects_page, projects):
    mock_get_projects_page.side_effect = [
        (25, projects[:25], False, 25),
        (25, projects[25:], True, -1),
    ]
    assert all([x == y for x, y in zip(projects, get_projects())])
    assert [call(25, 0), call(25, 25)] == mock_get_projects_page.mock_calls


@pytest.mark.parametrize("key, expected", [
    (False, 'k0: n0'),
    (True, 'k0'),
])
@patch('vang.bitbucket.get_projects.print')
@patch('vang.bitbucket.get_projects.get_projects', autospec=True)
def test_main(mock_get_projects, mock_print, key, expected, projects):
    mock_get_projects.return_value = projects
    main(key)
    assert [call(expected)] == mock_print.mock_calls[:1]


@pytest.mark.parametrize("args", [
    '-f',
    '1',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['', {
        'key': False,
    }],
    ['-k', {
        'key': True,
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
