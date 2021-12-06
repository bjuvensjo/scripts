from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_projects import get_projects
from vang.bitbucket.get_projects import main
from vang.bitbucket.get_projects import parse_args


@pytest.fixture
def projects():
    return [{'key': f'k{n}', 'name': f'n{n}'} for n in range(50)]


@patch('vang.bitbucket.get_projects.get_all')
def test_get_projects(mock_get_all, projects):
    mock_get_all.return_value = projects
    assert all([x == y for x, y in zip(projects, get_projects())])


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
