#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.get_default_branches import get_repo_default_branch
from vang.bitbucket.get_default_branches import get_default_branch
from vang.bitbucket.get_default_branches import main
from vang.bitbucket.get_default_branches import parse_args

import pytest


@pytest.fixture
def call_fixtures():
    return {
        'id': 'refs/heads/develop',
        'displayId': 'develop',
        'type': 'BRANCH',
        'latestCommit': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'latestChangeset': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'isDefault': True
    }


@patch('vang.bitbucket.get_default_branches.call')
def test_get_repo_default_branch(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures
    assert (['project_key', 'repo_slug'], {
        'displayId': 'develop',
        'id': 'refs/heads/develop',
        'isDefault': True,
        'latestChangeset': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'latestCommit': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'type': 'BRANCH'
    }) == get_repo_default_branch(['project_key', 'repo_slug'])


@patch('vang.bitbucket.get_default_branches.call')
def test_get_default_branch(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures
    assert [(['project_key', 'repo_slug'], {
        'displayId': 'develop',
        'id': 'refs/heads/develop',
        'isDefault': True,
        'latestChangeset': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'latestCommit': '9b56af5e9d9e8bb55d6b9b6065ef488e5449187c',
        'type': 'BRANCH'
    })] * 2 == get_default_branch([['project_key', 'repo_slug']] * 2)


@patch('vang.bitbucket.get_default_branches.print')
@patch('vang.bitbucket.get_default_branches.get_repo_specs')
@patch('vang.bitbucket.get_default_branches.call')
def test_main(mock_call, mock_get_repo_specs, mock_print, call_fixtures):
    mock_call.return_value = call_fixtures
    mock_get_repo_specs.return_value = [['project_key', 'repo_slug']] * 2
    main(['.'], None, ['project_key'] * 2)
    assert [
        call('project_key/repo_slug: develop'),
        call('project_key/repo_slug: develop')
    ] == mock_print.mock_calls
    assert [call(['.'], None, ['project_key', 'project_key'])
            ] == mock_get_repo_specs.mock_calls


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
    ['', {
        'dirs': ['.'],
        'projects': None,
        'repos': None,
    }],
    ['-d d1 d2', {
        'dirs': ['d1', 'd2'],
        'projects': None,
        'repos': None,
    }],
    ['-p p1 p2', {
        'dirs': ['.'],
        'projects': ['p1', 'p2'],
        'repos': None,
    }],
    [
        '-r p/r1 p/r2',
        {
            'dirs': ['.'],
            'projects': None,
            'repos': ['p/r1', 'p/r2'],
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
