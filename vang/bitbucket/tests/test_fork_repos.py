#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.fork_repos import fork_repo
from vang.bitbucket.fork_repos import fork_repos
from vang.bitbucket.fork_repos import main
from vang.bitbucket.fork_repos import parse_args

import pytest


@patch('vang.bitbucket.fork_repos.call')
def test_fork_repo(mock_call):
    mock_call.return_value = '"response"'
    assert (('project_key', 'repo_slug'), '"response"') == fork_repo(
        ('project_key', 'repo_slug'), 'fork_project_key')
    assert [
        call(
            '/rest/api/1.0/projects/project_key/repos/repo_slug',
            {"slug": "repo_slug", "project": {"key": "fork_project_key"}},
            'POST',
        )
    ] == mock_call.mock_calls


@patch('vang.bitbucket.fork_repos.fork_repo')
def test_fork_repos(mock_fork_repo):
    mock_fork_repo.side_effect = lambda x, y: (x, 'response')
    assert [(['project_key', 'repo_slug'], 'response'),
            (['project_key', 'repo_slug'], 'response')] == fork_repos(
                [['project_key', 'repo_slug'], ['project_key', 'repo_slug']],
                'fork_project_key',
            )


@patch('vang.bitbucket.fork_repos.print')
@patch('vang.bitbucket.fork_repos.fork_repos')
@patch('vang.bitbucket.fork_repos.get_repo_specs')
def test_main(mock_get_repo_specs, mock_fork_repos, mock_print):
    mock_get_repo_specs.return_value = [('d1', 'r1'), ('d2', 'r2')]
    mock_fork_repos.return_value = [
        (('d1', 'r1'), 'response1'),
        (('d2', 'r2'), 'response2'),
    ]
    main(
        'fork_project_key',
        ['d1', 'd2'],
        None,
        None,
    )
    assert [call(['d1', 'd2'], None, None)] == mock_get_repo_specs.mock_calls
    assert [
        call([('d1', 'r1'), ('d2', 'r2')], 'fork_project_key'),
    ] == mock_fork_repos.mock_calls
    assert [call('d1/r1: response1'),
            call('d2/r2: response2')] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '1 2',
    '1 -d d -r r',
    '1 -d d -p p',
    '1 -r r -p p',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        'fork_project_key -d d1 d2',
        {
            'fork_project': 'fork_project_key',
            'dirs': ['d1', 'd2'],
            'repos': None,
            'projects': None
        }
    ],
    [
        'fork_project_key -r key1/repo1 key2/repo2',
        {
            'fork_project': 'fork_project_key',
            'dirs': ['.'],
            'repos': ['key1/repo1', 'key2/repo2'],
            'projects': None
        }
    ],
    [
        'fork_project_key -p key1 key2',
        {
            'fork_project': 'fork_project_key',
            'dirs': ['.'],
            'repos': None,
            'projects': ['key1', 'key2']
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
