#!/usr/bin/env python3

from unittest.mock import call, patch

from pytest import raises

from vang.tfs.get_repos import get_repos, main, parse_args


def test_get_repos():
    assert [] == get_repos()
    with patch(
            'vang.tfs.get_repos.call',
            return_value={
                'value': [{
                    'name': 'name',
                    'remoteUrl': 'remoteUrl'
                }]
            },
    ):
        with patch(
                'vang.tfs.get_repos.get_projects',
                return_value=['organisation/project'],
        ):
            assert [(
                'organisation/project',
                {
                    'name': 'name',
                    'remoteUrl': 'remoteUrl'
                },
            )] == get_repos('organisation')
        assert [(
            'organisation/project',
            {
                'name': 'name',
                'remoteUrl': 'remoteUrl'
            },
        )] == get_repos(projects=['organisation/project'])
        assert ['name'] == get_repos(
            projects=['organisation/project'],
            names=True,
        )
        assert ['organisation/project/name'] == get_repos(
            projects=['organisation/project'],
            repo_specs=True,
        )
        assert ['remoteUrl'] == get_repos(
            projects=['organisation/project'],
            urls=True,
        )


def test_main():
    with patch(
            'vang.tfs.get_repos.get_repos',
            return_value=['repo1', 'repo2'],
    ) as mock_get_repos:
        with patch('vang.tfs.get_repos.print') as mock_print:
            main('organisations', 'projects', 'names', 'repo_specs', 'urls')
            assert [
                call('organisations', 'projects', 'names', 'repo_specs', 'urls')
            ] == mock_get_repos.mock_calls
            assert [call('repo1'), call('repo2')] == mock_print.mock_calls


def test_parse_args():
    for args in [
            None, '', '-o', '-p', '-o o -p p', '-o o -n -r', '-o o -n -u',
            '-o o -r -u', '-o o -n foo'
    ]:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        [
            '-o o1 o2',
            {
                'names': False,
                'organisations': ['o1', 'o2'],
                'projects': None,
                'repo_specs': False,
                'urls': False
            }
        ],
        [
            '-p o/p1 o/p2',
            {
                'names': False,
                'organisations': None,
                'projects': ['o/p1', 'o/p2'],
                'repo_specs': False,
                'urls': False
            }
        ],
        [
            '-o o -n',
            {
                'names': True,
                'organisations': ['o'],
                'projects': None,
                'repo_specs': False,
                'urls': False
            }
        ],
        [
            '-o o -r',
            {
                'names': False,
                'organisations': ['o'],
                'projects': None,
                'repo_specs': True,
                'urls': False
            }
        ],
        [
            '-o o -u',
            {
                'names': False,
                'organisations': ['o'],
                'projects': None,
                'repo_specs': False,
                'urls': True
            }
        ],
    ]:
        assert pargs == parse_args(args.split(' ')).__dict__
