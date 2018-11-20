#!/usr/bin/env python3
from unittest.mock import call, patch

from vang.bitbucket.utils import get_branch
from vang.bitbucket.utils import get_clone_url
from vang.bitbucket.utils import get_project_and_repo
from vang.bitbucket.utils import get_repo_specs


@patch(
    'vang.bitbucket.utils.run_command',
    return_value=(0, 'develop'),
    autospec=True)
def test_get_branch(mock_run_command):
    assert 'develop' == get_branch('clone_dir/.git')
    assert [call(
        'git rev-parse --abbrev-ref HEAD',
        True,
        'clone_dir/.git',
    )] == mock_run_command.mock_calls


@patch(
    'vang.bitbucket.utils.run_command',
    side_effect=[
        (0, 'http://myorg/stash/scm/project/repo.git'),
        (1, ''),
        (0, 'http://myorg/stash/scm/project/repo.git'),
    ],
    autospec=True)
def test_get_clone_url(mock_run_command):
    assert 'http://myorg/stash/scm/project/repo.git' == get_clone_url(
        'clone_dir/.git')
    assert 'http://myorg/stash/scm/project/repo.git' == get_clone_url(
        'clone_dir')
    assert [
        call('git --git-dir clone_dir/.git remote get-url origin', True,
             'clone_dir/.git', False),
        call('git --git-dir clone_dir remote get-url origin', True, 'clone_dir',
             False),
        call('git --git-dir clone_dir/.git remote get-url origin', True,
             'clone_dir')
    ] == mock_run_command.mock_calls


@patch(
    'vang.bitbucket.utils.get_clone_url',
    return_value='http://myorg/stash/scm/project/repo.git',
    autospec=True,
)
def test_get_project_and_repo(mock_get_clone_url):
    assert ('PROJECT', 'repo') == get_project_and_repo('clone_dir')
    assert [call('clone_dir')] == mock_get_clone_url.mock_calls


@patch(
    'vang.bitbucket.utils.get_project_and_repo',
    side_effect=[('PROJECT', 'r1'), ('PROJECT', 'r2')],
    autospec=True,
)
@patch(
    'vang.bitbucket.utils.get_all_repos',
    return_value=[('PROJECT', 'r1'), ('PROJECT', 'r2')],
    autospec=True,
)
def test_get_repo_specs(mock_get_all_repos, mock_get_project_and_repo):
    assert [('PROJECT', 'r1'), ('PROJECT', 'r2')] == list(
        get_repo_specs(['PROJECT/r1', 'PROJECT/r2']))

    assert [('PROJECT', 'r1'), ('PROJECT', 'r2')] == list(
        get_repo_specs(repos=['PROJECT/r1', 'PROJECT/r2']))

    assert [('PROJECT', 'r1'), ('PROJECT', 'r2')] == list(
        get_repo_specs(projects=['PROJECT']))

    assert [call(
        ['PROJECT'],
        max_processes=10,
        only_spec=True,
    )] == mock_get_all_repos.mock_calls

    assert [
        call('PROJECT/r1'),
        call('PROJECT/r2'),
    ] == mock_get_project_and_repo.mock_calls
