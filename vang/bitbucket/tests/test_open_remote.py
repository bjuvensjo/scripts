#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.open_remote import open_remote
from vang.bitbucket.open_remote import main
from vang.bitbucket.open_remote import parse_args

import pytest


@pytest.mark.parametrize("git_dir, repo, project, expected", [
    (
        '.',
        None,
        None,
        [
            call([
                'open', ''.join([
                    'base_url/projects/project_key/repos/repo_slug/commits?',
                    'until=refs%2Fheads%2Fdevelop&merges=include'
                ])
            ])
        ],
    ),
    (
        '.',
        'project_key/repo_slug',
        None,
        [
            call([
                'open', 'base_url/projects/project_key/repos/repo_slug/browse'
            ])
        ],
    ),
    (
        '.',
        None,
        'project_key',
        [call(['open', 'base_url/projects/project_key'])],
    ),
])
@patch('vang.bitbucket.open_remote.run', autospec=True)
@patch('vang.bitbucket.open_remote.get_branch', autospec=True)
@patch('vang.bitbucket.open_remote.get_project_and_repo', autospec=True)
def test_open_remote(
        mock_get_project_and_repo,
        mock_get_branch,
        mock_run,
        git_dir,
        repo,
        project,
        expected,
):
    mock_get_project_and_repo.return_value = ('project_key', 'repo_slug')
    mock_get_branch.return_value = 'develop'

    open_remote(git_dir, repo, project, 'base_url')
    assert expected == mock_run.mock_calls


@pytest.mark.parametrize("repo_dir, repo, project, expected", [
    (
        '.',
        None,
        None,
        [call('abspath', None, None)],
    ),
    (
        '.',
        'project_key/repo_slug',
        None,
        [call('abspath', 'project_key/repo_slug', None)],
    ),
    (
        '.',
        None,
        'project_key',
        [call('abspath', None, 'project_key')],
    ),
])
@patch('vang.bitbucket.open_remote.abspath', autospec=True)
@patch('vang.bitbucket.open_remote.open_remote', autospec=True)
def test_main(
        mock_open_remote,
        mock_abspath,
        repo_dir,
        repo,
        project,
        expected,
):
    mock_abspath.return_value = 'abspath'
    main(repo_dir, repo, project)
    assert expected == mock_open_remote.mock_calls
    assert [call('./.git')] == mock_abspath.mock_calls


@pytest.mark.parametrize("args", [
    '1'
    '-d d -r r',
    '-d d -p p',
    '-r r -p p',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['', {
        'repo_dir': '.',
        'repo': None,
        'project': None,
    }],
    ['-d d', {
        'repo_dir': 'd',
        'repo': None,
        'project': None,
    }],
    ['-r r', {
        'repo_dir': '.',
        'repo': 'r',
        'project': None,
    }],
    ['-p p', {
        'repo_dir': '.',
        'repo': None,
        'project': 'p',
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
