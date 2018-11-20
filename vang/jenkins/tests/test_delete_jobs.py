#!/usr/bin/env python3
from unittest.mock import patch, call

from pytest import raises

from vang.jenkins.delete_jobs import delete_jobs
from vang.jenkins.delete_jobs import main
from vang.jenkins.delete_jobs import parse_args


@patch('vang.jenkins.delete_jobs.call', autospec=True)
def test_delete_jobs(mock_call):
    mock_call.return_value = 201

    assert [('j1', 201), ('j2', 201)] == delete_jobs(['j1', 'j2'])
    assert [
        call('/job/j1/doDelete', method='POST', only_response_code=True),
        call('/job/j2/doDelete', method='POST', only_response_code=True)
    ] == mock_call.mock_calls


def test_parse_args():
    for args in ['']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        ['j1 j2', {
            'job_names': ['j1', 'j2']
        }],
    ]:
        assert pargs == parse_args(args.split(' ') if args else '').__dict__


@patch('vang.jenkins.delete_jobs.print')
@patch('vang.jenkins.delete_jobs.delete_jobs', autospec=True)
def test_main(mock_delete_jobs, mock_print):
    mock_delete_jobs.return_value = [('j1', 201), ('j2', 201)]

    main(['j1', 'j2'])
    assert [call(['j1', 'j2'])] == mock_delete_jobs.mock_calls
    assert [call('j1', 201), call('j2', 201)] == mock_print.mock_calls
