#!/usr/bin/env python3
from os import environ
from unittest.mock import call, patch

from pytest import raises

from vang.maven.switch_settings import main
from vang.maven.switch_settings import parse_args
from vang.maven.switch_settings import switch_settings

import pytest


@patch(
    'vang.maven.switch_settings.exists',
    autospec=True,
    side_effect=(False, True))
@patch(
    'vang.maven.switch_settings.run_command',
    autospec=True,
    return_value=(0, ''))
def test_switch_settings(mock_run_command, mock_exists):
    with raises(ValueError):
        switch_settings('not_exists')
    assert (0, '') == switch_settings('exists')

    home = environ["HOME"]
    assert [
        call(f'{home}/.m2/settings_not_exists.xml'),
        call(f'{home}/.m2/settings_exists.xml')
    ] == mock_exists.mock_calls
    assert [
        call(f'ln -sf {home}/.m2/settings_exists.xml {home}/.m2/settings.xml',
             True)
    ] == mock_run_command.mock_calls


@pytest.mark.parametrize("name, switch_setting_calls, print_calls", [
    (
        'posix',
        [call('project')],
        [call('')],
    ),
    (
        'not posix',
        [],
        [
            call('Platform not supported. '
                 'Please implement, and make a pull request.')
        ],
    ),
])
@patch('vang.maven.switch_settings.print')
@patch(
    'vang.maven.switch_settings.switch_settings',
    return_value=(0, ''),
    autospec=True)
def test_main(mock_switch_settings, mock_print, name, switch_setting_calls,
              print_calls):
    with patch('vang.maven.switch_settings.name', name):
        main('project')
        assert switch_setting_calls == mock_switch_settings.mock_calls
        assert print_calls == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    'foo bar',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        'project',
        {
            'ending': 'project'
        },
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
