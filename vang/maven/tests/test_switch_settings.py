#!/usr/bin/env python3
from os import environ
from unittest.mock import call, patch

from pytest import raises

from vang.maven.switch_settings import main
from vang.maven.switch_settings import parse_args
from vang.maven.switch_settings import switch_settings


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


@patch('vang.maven.switch_settings.print')
@patch(
    'vang.maven.switch_settings.switch_settings',
    return_value=(0, ''),
    autospec=True)
def test_main(mock_switch_settings, mock_print):
    with patch('vang.maven.switch_settings.name', 'posix'):
        main('project')
        assert [call('project')] == mock_switch_settings.mock_calls
        assert [call('')] == mock_print.mock_calls

    with patch('vang.maven.switch_settings.name', 'not posix'):
        mock_switch_settings.reset_mock()
        mock_print.reset_mock()
        main('project')
        assert [] == mock_switch_settings.mock_calls
        assert [
            call('Platform not supported. '
                 'Please implement, and make a pull request.')
        ] == mock_print.mock_calls


def test_parse_args():
    for args in ['', 'foo bar']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        [
            'project',
            {
                'ending': 'project'
            },
        ],
    ]:
        assert pargs == parse_args(args.split(' ')).__dict__
