#!/usr/bin/env python3
from unittest.mock import patch, call

from pytest import raises

from vang.jenkins.get_jobs import get_jobs
from vang.jenkins.get_jobs import main
from vang.jenkins.get_jobs import map_color
from vang.jenkins.get_jobs import parse_args
from vang.jenkins.get_jobs import FAILURE
from vang.jenkins.get_jobs import SUCCESS

import pytest


def test_map_color():
    assert SUCCESS == map_color('blue')
    assert FAILURE == map_color('not_blue')


@pytest.mark.parametrize("statuses, only_names, expected", [
    ([SUCCESS, FAILURE], False, [
        {
            'color': 'blue',
            'name': 'success'
        },
        {
            'color': 'not_blue',
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
            'color': 'not_blue'
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
        }
    ],
    [
        '-n -f',
        {
            'only_failures': True,
            'only_names': True,
            'only_successes': False,
        }
    ],
    [
        '-n -s',
        {
            'only_failures': False,
            'only_names': True,
            'only_successes': True,
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__


@pytest.mark.parametrize(
    "only_failures, only_successes, only_names, expected", [
        (False, False, True, [call(['FAILURE', 'SUCCESS'], True)]),
        (True, False, True, [call(['FAILURE'], True)]),
        (False, True, True, [call(['SUCCESS'], True)]),
    ])
@patch('vang.jenkins.get_jobs.print')
@patch('vang.jenkins.get_jobs.get_jobs', autospec=True)
def test_main(mock_get_jobs, mock_print, only_failures, only_successes,
              only_names, expected):
    mock_get_jobs.return_value = ['job']

    main(only_failures, only_successes, only_names)
    assert expected == mock_get_jobs.mock_calls
    assert [call('job')] == mock_print.mock_calls
