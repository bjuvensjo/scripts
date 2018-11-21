#!/usr/bin/env python3
from unittest.mock import patch, call

from pytest import raises

from vang.jenkins.trigger_builds import trigger_builds
from vang.jenkins.trigger_builds import main
from vang.jenkins.trigger_builds import parse_args

import pytest


@patch('vang.jenkins.trigger_builds.call', autospec=True)
def test_trigger_builds(mock_call):
    mock_call.return_value = 201

    assert [('j1', 201), ('j2', 201)] == trigger_builds(['j1', 'j2'])
    assert [
        call('/job/j1/build', method='POST', only_response_code=True),
        call('/job/j2/build', method='POST', only_response_code=True)
    ] == mock_call.mock_calls


@pytest.mark.parametrize("args", [
    '',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['j1 j2', {
        'job_names': ['j1', 'j2']
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__


@patch('vang.jenkins.trigger_builds.print')
@patch('vang.jenkins.trigger_builds.trigger_builds', autospec=True)
def test_main(mock_trigger_builds, mock_print):
    mock_trigger_builds.return_value = [('j1', 201), ('j2', 201)]

    main(['j1', 'j2'])
    assert [call(['j1', 'j2'])] == mock_trigger_builds.mock_calls
    assert [call('j1', 201), call('j2', 201)] == mock_print.mock_calls
