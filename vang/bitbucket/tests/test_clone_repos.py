#!/usr/bin/env python3
from unittest.mock import MagicMock, call, patch

import pytest
from more_itertools import take
from pytest import raises

from vang.bitbucket.clone_repos import clone
from vang.bitbucket.clone_repos import get_config_commands
from vang.bitbucket.clone_repos import get_projects_commands
from vang.bitbucket.clone_repos import get_repos_commands
from vang.bitbucket.clone_repos import main
from vang.bitbucket.clone_repos import parse_args
from vang.bitbucket.clone_repos import should_be_cloned


@patch('vang.bitbucket.clone_repos.is_included', return_value=True)
def test_should_be_cloned(mock_is_included):
    mock_has_branch_map = MagicMock(return_value=True)
    assert should_be_cloned(
        'project',
        'repo',
        {
            'includes': ['includes'],
            'excludes': ['excludes']
        },
        mock_has_branch_map,
    )
    assert [call('repo', ['excludes'],
                 ['includes'])] == mock_is_included.mock_calls


@patch('vang.bitbucket.clone_repos.run_commands', return_value=iter([1, 2, 3]))
@patch('vang.bitbucket.clone_repos.makedirs')
def test_clone(mock_makedirs, mock_run_commands):
    assert [1, 2, 3] == take(3, clone(['commands'], 'root_dir'))
    assert [call('root_dir', exist_ok=True)] == mock_makedirs.mock_calls
    assert [
        call([('commands', 'root_dir')],
             check=False,
             max_processes=25,
             timeout=60)
    ] == mock_run_commands.mock_calls


@patch(
    'vang.bitbucket.clone_repos.get_clone_urls',
    return_value=[[
        'clone_dir',
        'project',
        'repo',
        'command',
    ]])
def test_get_projects_commands(mock_get_clone_urls):
    assert [('clone_dir', 'project', 'repo', 'command')] == list(
        get_projects_commands('projects', 'branch'))
    assert [call('projects', True, 'branch',
                 False)] == mock_get_clone_urls.mock_calls


@patch('builtins.print')
@patch(
    'vang.bitbucket.clone_repos.get_clone_urls',
    return_value=[
        ['clone_dir', 'project', 'repo1', 'command'],
        ['clone_dir', 'project', 'repo2', 'command'],
    ])
def test_get_repos_commands(mock_get_clone_urls, mock_print):
    assert [
        ('clone_dir', 'project', 'repo1', 'command'),
        ('clone_dir', 'project', 'repo2', 'command'),
    ] == get_repos_commands([
        'project/repo1',
        'project/repo2',
        'project/non_existing_repo',
    ], 'branch')
    assert [call({'project'}, True, 'branch',
                 False)] == mock_get_clone_urls.mock_calls
    assert [call('Warning! Non existing repo: project/non_existing_repo')
            ] == mock_print.mock_calls


@patch('vang.bitbucket.clone_repos.should_be_cloned', return_value=True)
@patch(
    'vang.bitbucket.clone_repos.get_clone_urls',
    return_value=[
        ['clone_dir', 'project', 'repo1', 'command'],
        ['clone_dir', 'project', 'repo2', 'command'],
    ])
@patch(
    'vang.bitbucket.clone_repos.has_branch',
    return_value=[[('project', 'repo1'), True], [('project', 'repo2'), False]])
def test_get_config_commands(mock_has_branch, mock_get_clone_urls,
                             mock_should_be_cloned):
    assert [
        ('clone_dir', 'project', 'repo1', 'command'),
        ('clone_dir', 'project', 'repo2', 'command'),
    ] == list(
        get_config_commands({
            'projects': {
                'project': 'project'
            },
            'branch': 'branch'
        }))
    assert [call([('project', 'repo1'), ('project', 'repo2')],
                 'branch')] == mock_has_branch.mock_calls
    assert [call(
        {
            'project': 'project'
        },
        True,
        'branch',
        False,
    )] == mock_get_clone_urls.mock_calls
    assert [
        call(
            'project',
            'repo1',
            'project',
            {
                ('project', 'repo1'): True,
                ('project', 'repo2'): False
            },
        ),
        call(
            'project',
            'repo2',
            'project',
            {
                ('project', 'repo1'): True,
                ('project', 'repo2'): False
            },
        )
    ] == mock_should_be_cloned.mock_calls


@patch('builtins.open')
@patch('builtins.print')
@patch('vang.bitbucket.clone_repos.clone')
@patch('vang.bitbucket.clone_repos.get_config_commands')
@patch('vang.bitbucket.clone_repos.get_projects_commands')
@patch('vang.bitbucket.clone_repos.get_repos_commands')
@patch('vang.bitbucket.clone_repos.load')
def test_main(
        mock_load,
        mock_get_repos_commands,
        mock_get_projects_commands,
        mock_get_config_commands,
        mock_clone,
        mock_print,
        mock_open,
):
    mock_load.return_value = 'load'
    mock_process = MagicMock()
    mock_process.stdout.decode.return_value = 'Cloned...'
    mock_clone.return_value = [mock_process]
    commands = [
        ['clone_dir', 'project', 'repo1', 'command'],
        ['clone_dir', 'project', 'repo2', 'command'],
    ]
    mock_get_config_commands.return_value = commands
    mock_get_projects_commands.return_value = commands
    mock_get_repos_commands.return_value = commands

    assert not main('root_dir', projects=['project'], branch='branch')
    assert [call(
        ['project'],
        'branch',
        False,
    )] == mock_get_projects_commands.mock_calls
    assert [call(['command', 'command'], 'root_dir')] == mock_clone.mock_calls
    assert [call('01', 'Cloned...', end='')] == mock_print.mock_calls

    assert not main('root_dir', repos=['repos'], branch='branch')
    assert [call(
        ['repos'],
        'branch',
        False,
    )] == mock_get_repos_commands.mock_calls

    assert not main('root_dir', config='config', branch='branch')
    assert [
        call('config', 'rt', encoding='utf-8'),
        call().__enter__(),
        call().__exit__(None, None, None)
    ] == mock_open.mock_calls
    assert [call(
        'load',
        'branch',
        False,
    )] == mock_get_config_commands.mock_calls


@pytest.mark.parametrize("args", [
    '',
    'foo',
    '-p p -r r',
    '-p p -c c',
    '-r r -c c',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        '-p p1 p2',
        {
            'branch': None,
            'config': None,
            'root_dir': '.',
            'flat': False,
            'projects': ['p1', 'p2'],
            'repos': None
        }
    ],
    [
        '-r r1 r2',
        {
            'branch': None,
            'config': None,
            'root_dir': '.',
            'flat': False,
            'projects': None,
            'repos': ['r1', 'r2']
        }
    ],
    [
        '-c c',
        {
            'branch': None,
            'config': 'c',
            'root_dir': '.',
            'flat': False,
            'projects': None,
            'repos': None
        }
    ],
    [
        '-c c -b b -d d -f',
        {
            'branch': 'b',
            'config': 'c',
            'root_dir': 'd',
            'flat': True,
            'projects': None,
            'repos': None
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
