#!/usr/bin/env python3
from unittest.mock import patch, call

from pytest import raises

from vang.jenkins.get_jobs import get_jobs
from vang.jenkins.get_jobs import main
from vang.jenkins.get_jobs import map_color
from vang.jenkins.get_jobs import parse_args
from vang.jenkins.get_jobs import FAILURE
from vang.jenkins.get_jobs import SUCCESS


def test_map_color():
    assert SUCCESS == map_color('blue')
    assert FAILURE == map_color('not_blue')


@patch('vang.jenkins.get_jobs.call', autospec=True)
def test_get_jobs(mock_call):
    mock_call.return_value = {
        'jobs': [{
            'name': 'success',
            'color': 'blue'
        }, {
            'name': 'failure',
            'color': 'not_blue'
        }]
    }

    assert [
        {
            'color': 'blue',
            'name': 'success'
        },
        {
            'color': 'not_blue',
            'name': 'failure'
        },
    ] == get_jobs()
    assert [call('/api/json')] == mock_call.mock_calls

    assert ['success', 'failure'] == get_jobs(only_names=True)

    assert ['success'] == get_jobs(statuses=[SUCCESS], only_names=True)

    assert ['failure'] == get_jobs(statuses=[FAILURE], only_names=True)


def test_parse_args():
    for args in ['1', '-f f -s s']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
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
    ]:
        assert pargs == parse_args(args.split(' ') if args else '').__dict__


@patch('vang.jenkins.get_jobs.print')
@patch('vang.jenkins.get_jobs.get_jobs', autospec=True)
def test_main(mock_get_jobs, mock_print):
    mock_get_jobs.return_value = ['job']

    main(False, False, True)
    assert [call(['FAILURE', 'SUCCESS'], True)] == mock_get_jobs.mock_calls
    assert [call('job')] == mock_print.mock_calls

    mock_get_jobs.reset_mock()
    main(True, False, True)
    assert [call(['FAILURE'], True)] == mock_get_jobs.mock_calls

    mock_get_jobs.reset_mock()
    main(False, True, True)
    assert [call(['SUCCESS'], True)] == mock_get_jobs.mock_calls
