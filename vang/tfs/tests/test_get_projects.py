#!/usr/bin/env python3

from unittest.mock import call, patch

from pytest import raises

from vang.tfs.get_projects import get_projects, main, parse_args


def test_get_projects():
    assert [] == get_projects(None)
    assert [] == get_projects([])
    with patch(
            'vang.tfs.get_projects.call',
            return_value={
                'count':
                1,
                'value': [{
                    'id': 'id',
                    'name': 'project',
                    'revision': 272509,
                    'state': 'wellFormed',
                    'url': 'remoteUrl',
                    'visibility': 'private'
                }]
            },
    ):
        assert [('organisation', {
            'id': 'id',
            'name': 'project',
            'revision': 272509,
            'state': 'wellFormed',
            'url': 'remoteUrl',
            'visibility': 'private'
        })] == get_projects(['organisation'])
        assert ['organisation/project'] == get_projects(['organisation'],
                                                        project_specs=True)
        assert ['project'] == get_projects(['organisation'], names=True)
        assert ['project'] == get_projects(['organisation'],
                                           project_specs=True,
                                           names=True)


def test_parse_args():
    for args in [None, '', '-n n -p -p']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        [
            'o1 o2',
            {
                'names': False,
                'organisations': ['o1', 'o2'],
                'project_specs': False
            }
        ],
        [
            'o1 -n',
            {
                'names': True,
                'organisations': ['o1'],
                'project_specs': False
            }
        ],
        [
            'o1 -p',
            {
                'names': False,
                'organisations': ['o1'],
                'project_specs': True
            }
        ],
    ]:
        assert pargs == parse_args(args.split(' ')).__dict__


def test_main():
    with patch(
            'vang.tfs.get_projects.get_projects',
            return_value=['project1', 'project2'],
    ) as mock_get_projects:
        with patch('vang.tfs.get_projects.print') as mock_print:
            main('organisations', False, True)
            assert [call('organisations', False,
                         True)] == mock_get_projects.mock_calls
            assert [call('project1'), call('project2')] == mock_print.mock_calls
