#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.fork_repos_git import fork_repo
from vang.bitbucket.fork_repos_git import fork_repos
from vang.bitbucket.fork_repos_git import main
from vang.bitbucket.fork_repos_git import parse_args

import pytest


@patch('vang.bitbucket.fork_repos_git.print')
@patch('vang.bitbucket.fork_repos_git.set_repo_default_branch')
@patch('vang.bitbucket.fork_repos_git.create_repo')
@patch('vang.bitbucket.fork_repos_git.run_command')
def test_fork_repo(
        mock_run_command,
        mock_create_repo,
        mock_set_repo_default_branch,
        mock_print,
):
    mock_run_command.return_value = (
        0, 'http://myorg/stash/scm/project_key/repo_slug.git')

    assert (
        ('fork_project_key', 'repo_slug'),
        'http://myorg/stash/scm/fork_project_key/repo_slug.git') == fork_repo(
            'fork_project_key', ['develop', 'master'], '/project_key/repo_slug')

    assert [call(('fork_project_key', 'repo_slug'),
                 'develop')] == mock_set_repo_default_branch.mock_calls
    assert [call('fork_project_key',
                 'repo_slug')] == mock_create_repo.mock_calls
    assert [
        call(
            'git checkout master',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git checkout develop',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git remote get-url origin',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git remote set-url origin http://myorg/'
            'stash/scm/fork_project_key/repo_slug.git',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git remote prune origin',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git push -u origin develop',
            cwd='/project_key/repo_slug',
            return_output=True),
        call(
            'git push -u origin master',
            cwd='/project_key/repo_slug',
            return_output=True)
    ] == mock_run_command.mock_calls


@patch('vang.bitbucket.fork_repos_git.fork_repo')
@patch('vang.bitbucket.fork_repos_git.get_work_dirs')
@patch('vang.bitbucket.fork_repos_git.clone_repos.main')
def test_fork_repos(mock_main, mock_get_work_dirs, mock_fork_repo):
    mock_get_work_dirs.return_value = ('d1', 'd2')
    mock_fork_repo.side_effect = lambda x, y, z: (x, y, z)
    fork_repos('fork_project_key', ['develop', 'master'], 'work_dir', None,
               ['p1', 'p2'])
    assert [call('work_dir', ['p1', 'p2'], None,
                 branch='develop', flat=True)] == mock_main.mock_calls
    assert [call('.git/', 'work_dir')] == mock_get_work_dirs.mock_calls
    assert [
        call('fork_project_key', ['develop', 'master'], 'd1'),
        call('fork_project_key', ['develop', 'master'], 'd2')
    ] == mock_fork_repo.mock_calls


@pytest.mark.parametrize("repos, projects, expected", [
    (['key1/repo1', 'key2/repo2'], None, [
        call(
            'fork_project_key',
            ['develop', 'master'],
            '/work_dir',
            ['key1/repo1', 'key2/repo2'],
            None,
        ),
    ]),
    (None, ['key1', 'key2'], [
        call(
            'fork_project_key',
            ['develop', 'master'],
            '/work_dir',
            None,
            ['key1', 'key2'],
        )
    ]),
])
@patch('vang.bitbucket.fork_repos_git.fork_repos')
def test_main(mock_fork_repos, repos, projects, expected):
    main(
        'fork_project_key',
        ['develop', 'master'],
        '/work_dir',
        repos,
        projects,
    )
    assert expected == mock_fork_repos.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '1',
    '1 2',
    '1 -r -p',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        'fork_project_key -r key1/repo1 key2/repo2',
        {
            'fork_project': 'fork_project_key',
            'branches': ['develop'],
            'work_dir': '.',
            'repos': ['key1/repo1', 'key2/repo2'],
            'projects': None
        }
    ],
    [
        'fork_project_key -d d -b d m -p key1 key2',
        {
            'fork_project': 'fork_project_key',
            'branches': ['d', 'm'],
            'work_dir': 'd',
            'repos': None,
            'projects': ['key1', 'key2']
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
