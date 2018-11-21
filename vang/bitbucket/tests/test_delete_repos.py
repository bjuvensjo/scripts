from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.delete_repos import delete_repo
from vang.bitbucket.delete_repos import delete_repos
from vang.bitbucket.delete_repos import main
from vang.bitbucket.delete_repos import parse_args

import pytest


@patch(
    'vang.bitbucket.delete_repos.call',
    return_value={
        'context': None,
        'message': 'Repository scheduled for deletion.',
        'exceptionName': None,
    })
def test_delete_repo(mock_call):
    assert (('project', 'repo'), {
        'context': None,
        'exceptionName': None,
        'message': 'Repository scheduled for deletion.',
    }) == delete_repo(('project', 'repo'))
    assert [call('/rest/api/1.0/projects/project/repos/repo',
                 method='DELETE')] == mock_call.mock_calls


@patch('vang.bitbucket.delete_repos.delete_repo', return_value=1)
def test_delete_repos(mock_delete_repo):
    assert [1, 1] == delete_repos([
        ('project', 'repo1'),
        ('project', 'repo2'),
    ])
    assert [call(('project', 'repo1')),
            call(('project', 'repo2'))] == mock_delete_repo.mock_calls


@patch('builtins.print')
@patch(
    'vang.bitbucket.delete_repos.delete_repos',
    side_effect=[[
        [('project', 'repo1'), 'deleted'],
        [('project', 'repo1'), 'deleted'],
    ]])
@patch(
    'vang.bitbucket.delete_repos.get_repo_specs',
    return_value=[
        ('project', 'repo1'),
        ('project', 'repo2'),
    ])
def test_main(mock_get_repo_specs, mock_delete_repos, mock_print):
    assert not main(dirs=None, projects=['project'])
    assert [call(None, None, ['project'])] == mock_get_repo_specs.mock_calls
    assert [call([
        ('project', 'repo1'),
        ('project', 'repo2'),
    ])] == mock_delete_repos.mock_calls
    assert [
        call('project/repo1: deleted'),
        call('project/repo1: deleted'),
    ] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    'foo',
    '-d d -r r',
    '-d d -p p',
    '-r r -p p',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['', {
        'dirs': ['.'],
        'projects': None,
        'repos': None
    }],
    ['-d d', {
        'dirs': ['d'],
        'projects': None,
        'repos': None
    }],
    ['-r r', {
        'dirs': ['.'],
        'projects': None,
        'repos': ['r']
    }],
    ['-p p', {
        'dirs': ['.'],
        'projects': ['p'],
        'repos': None
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
