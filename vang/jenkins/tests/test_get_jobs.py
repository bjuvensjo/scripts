#!/usr/bin/env python3
from unittest.mock import patch, call

import pytest
from pytest import raises

from vang.jenkins.get_jobs import FAILURE
from vang.jenkins.get_jobs import SUCCESS
from vang.jenkins.get_jobs import get_jobs, NOT_BUILT, UNKNOWN
from vang.jenkins.get_jobs import main
from vang.jenkins.get_jobs import map_color
from vang.jenkins.get_jobs import parse_args


def test_map_color():
    assert SUCCESS == map_color('blue')
    assert NOT_BUILT == map_color('notbuilt')
    assert FAILURE == map_color('red')
    assert UNKNOWN == map_color('')
    assert UNKNOWN == map_color('x')


@pytest.mark.parametrize("statuses, only_names, expected", [
    ([SUCCESS, FAILURE], False, [
        {
            'color': 'blue',
            'name': 'success'
        },
        {
            'color': 'red',
            'name': 'failure'
        },
    ]),
    ([SUCCESS, FAILURE], True, ['success', 'failure']),
    ([SUCCESS], True, ['success']),
    ([FAILURE], True, ['failure']),
])
@patch('vang.jenkins.get_jobs.call', autospec=True)
def test_get_jobs(mock_call, statuses, only_names, expected):
    mock_call.return_value = {
        'jobs': [{
            'name': 'success',
            'color': 'blue'
        }, {
            'name': 'failure',
            'color': 'red'
        }]
    }

    assert expected == get_jobs(statuses, only_names)
    assert [call('/api/json')] == mock_call.mock_calls


@pytest.mark.parametrize("args", [
    '1',
    '-f f -s s',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        '',
        {
            'only_failures': False,
            'only_names': False,
            'only_successes': False,
            'only_not_built': False,
            'only_unknown': False,
        }
    ],
    [
        '-n -f',
        {
            'only_failures': True,
            'only_names': True,
            'only_successes': False,
            'only_not_built': False,
            'only_unknown': False,
        }
    ],
    [
        '-n -s',
        {
            'only_failures': False,
            'only_names': True,
            'only_successes': True,
            'only_not_built': False,
            'only_unknown': False,
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__


@pytest.mark.parametrize(
    "only_failures, only_successes, only_names, only_not_built, only_unknown, expected", [
        (False, False, True, False, False, [call(['FAILURE', 'SUCCESS', 'NOT_BUILT', 'UNKNOWN'], True)]),
        (True, False, True, False, False, [call(['FAILURE'], True)]),
        (False, True, True, False, False, [call(['SUCCESS'], True)]),
    ])
@patch('vang.jenkins.get_jobs.print')
@patch('vang.jenkins.get_jobs.get_jobs', autospec=True)
def test_main(mock_get_jobs, mock_print, only_failures, only_successes,
              only_names, only_not_built, only_unknown, expected):
    mock_get_jobs.return_value = ['job']

    main(only_failures, only_successes, only_names, only_not_built, only_unknown)
    assert expected == mock_get_jobs.mock_calls
    assert [call('job')] == mock_print.mock_calls
