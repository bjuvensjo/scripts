#!/usr/bin/env python3

from unittest.mock import MagicMock, call, patch

import pytest
from pytest import raises

from vang.tfs.clone_repos import clone, main
from vang.tfs.clone_repos import clone_repos
from vang.tfs.clone_repos import get_clone_specs
from vang.tfs.clone_repos import get_commands
from vang.tfs.clone_repos import parse_args


@patch(
    'vang.tfs.clone_repos.run_commands', autospec=True, return_value=range(3))
@patch('vang.tfs.clone_repos.makedirs', autospec=True)
def test_clone(mock_makedirs, mock_run_commands):
    assert [0, 1, 2] == list(clone(['c1', 'c2'], 'root_dir'))
    assert [call('root_dir', exist_ok=True)] == mock_makedirs.mock_calls
    assert [
        call([('c1', 'root_dir'), ('c2', 'root_dir')],
             check=False,
             max_processes=5,
             timeout=180)
    ] == mock_run_commands.mock_calls


@pytest.mark.parametrize("clone_specs, branch, flat, expected", [
    (
        [['url1', 'clone_dir1'], ['url2', 'clone_dir2']],
        'branch',
        False,
        [
            'git clone url1 -b branch clone_dir1',
            'git clone url2 -b branch clone_dir2',
        ],
    ),
    (
        [['url1', 'clone_dir1'], ['url2', 'clone_dir2']],
        None,
        True,
        [
            'git clone url1',
            'git clone url2',
        ],
    ),
])
def test_get_commands(clone_specs, branch, flat, expected):
    assert expected == get_commands(clone_specs, branch, flat)


@patch('vang.tfs.clone_repos.get_repos', autospec=True)
def test_get_clone_specs(mock_get_repos):
    mock_get_repos.return_value = [[
        'project', {
            'name': 'name',
            'remoteUrl': 'remoteUrl'
        }
    ]]
    assert [('remoteUrl', 'project/name')] == get_clone_specs('projects', False)
    assert [('remoteUrl', 'name')] == get_clone_specs('projects', True)


@patch('vang.tfs.clone_repos.print')
@patch('vang.tfs.clone_repos.clone', autospec=True)
@patch('vang.tfs.clone_repos.get_clone_specs', autospec=True)
@patch('vang.tfs.clone_repos.get_projects', autospec=True)
def test_clone_repos(
        mock_get_projects,
        mock_get_clone_specs,
        mock_clone,
        mock_print,
):
    organisations = ['o1', 'o2']
    projects = ['o1/p', 'o2/p']
    repos = ['o1/p/r1', 'o1/p/r2']
    mock_get_projects.return_value = projects
    mock_get_clone_specs.return_value = [('remoteUrl1', 'r1'),
                                         ('remoteUrl2', 'r2')]
    process_mock = MagicMock()
    process_mock.stdout.decode.return_value = 'decode'
    mock_clone.return_value = [process_mock] * 2

    # organisations
    assert [
        ('remoteUrl1', 'r1'),
        ('remoteUrl2', 'r2'),
    ] == clone_repos(
        'root_dir',
        organisations=organisations,
        flat=True,
    )
    assert [
        call(['o1', 'o2'], project_specs=True),
    ] == mock_get_projects.mock_calls
    assert [
        call(['o1/p', 'o2/p'], True),
    ] == mock_get_clone_specs.mock_calls
    assert [
        call(['git clone remoteUrl1', 'git clone remoteUrl2'], 'root_dir'),
    ] == mock_clone.mock_calls
    assert [
        call('01', 'decode', end=''),
        call('02', 'decode', end=''),
    ] == mock_print.mock_calls

    # projects
    mock_get_clone_specs.reset_mock()
    mock_clone.reset_mock()
    assert [
        ('remoteUrl1', 'r1'),
        ('remoteUrl2', 'r2'),
    ] == clone_repos(
        'root_dir', projects=projects)
    assert [
        call(['o1/p', 'o2/p'], False),
    ] == mock_get_clone_specs.mock_calls
    assert [
        call(['git clone remoteUrl1 r1', 'git clone remoteUrl2 r2'],
             'root_dir'),
    ] == mock_clone.mock_calls

    # repos
    mock_get_clone_specs.reset_mock()
    mock_clone.reset_mock()
    assert [
        ('remoteUrl1', 'r1'),
        ('remoteUrl2', 'r2'),
    ] == clone_repos(
        'root_dir',
        repos=repos,
        flat=True,
    )
    assert [
        call({'o1/p'}, True),
    ] == mock_get_clone_specs.mock_calls
    assert [
        call(['git clone remoteUrl1', 'git clone remoteUrl2'], 'root_dir'),
    ] == mock_clone.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '-o o -p p',
    '-o o -r r',
    '-p p -r r',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        '-o organisation/project/repo',
        {
            'branch': None,
            'clone_dir': '.',
            'flat': False,
            'organisations': ['organisation/project/repo'],
            'projects': None,
            'repos': None
        }
    ],
    [
        '-p project/repo',
        {
            'branch': None,
            'clone_dir': '.',
            'flat': False,
            'organisations': None,
            'projects': ['project/repo'],
            'repos': None
        }
    ],
    [
        '-r repo',
        {
            'branch': None,
            'clone_dir': '.',
            'flat': False,
            'organisations': None,
            'projects': None,
            'repos': ['repo']
        }
    ],
    [
        '-r repo -b b -d d -f',
        {
            'branch': 'b',
            'clone_dir': 'd',
            'flat': True,
            'organisations': None,
            'projects': None,
            'repos': ['repo']
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__


@patch('vang.tfs.clone_repos.print')
@patch('vang.tfs.clone_repos.clone_repos', autospec=True)
def test_main(mock_clone_repos, mock_print):
    mock_clone_repos.return_value = [[0, 'r1'], [1, 'r2']]
    main(
        'clone_dir',
        ['organisations'],
        ['projects'],
        ['repos'],
        'branch',
        True,
    )
    assert [call('r1'), call('r2')] == mock_print.mock_calls
