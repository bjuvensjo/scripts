#!/usr/bin/env python3
from subprocess import CalledProcessError

from unittest.mock import MagicMock, call, patch

from vang.pio.shell import run_command
from vang.pio.shell import run_commands

import pytest


@pytest.mark.parametrize("return_output, expected", [(False, 0),
                                                     (True, (0, 'response'))])
@patch('vang.pio.shell.run')
def test_run_command(mock_run, return_output, expected):
    mock_run.return_value = MagicMock(returncode=0, stdout=b'response')
    assert expected == run_command('command', return_output, 'cwd', True, 1)
    assert [
        call(
            'command',
            check=True,
            cwd='cwd',
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=1,
        )
    ] == mock_run.mock_calls


@patch('vang.pio.shell.run')
def test_run_commands(mock_run):
    mock_run.side_effect = (
        MagicMock(returncode=0, stdout=b'response1'),
        MagicMock(returncode=0, stdout=b'response2'),
    )
    assert [(0, 'response1'), (0, 'response2')] == [(cp.returncode,
                                                     cp.stdout.decode().strip())
                                                    for cp in run_commands(
                                                        (
                                                            ('pwd', 'dir'),
                                                            ('ls', 'dir'),
                                                        ),
                                                        3,
                                                        True,
                                                        1,
                                                    )]
    mock_run.assert_has_calls(
        [
            call(
                'pwd',
                check=True,
                cwd='dir',
                shell=True,
                stderr=-2,
                stdout=-1,
                timeout=1,
            ),
            call(
                'ls',
                check=True,
                cwd='dir',
                shell=True,
                stderr=-2,
                stdout=-1,
                timeout=1,
            )
        ],
        any_order=True,
    )
    assert 2 == mock_run.call_count


@patch('vang.pio.shell.run')
def test_run_commands_raise(mock_run):
    mock_run.side_effect = (
        MagicMock(returncode=0, stdout=b'response1'),
        CalledProcessError(127, 'foo'),
        MagicMock(returncode=0, stdout=b'response2'),
    )

    try:
        list(
            run_commands(
                (
                    ('pwd', 'dir'),
                    ('foo', 'dir'),
                    ('ls', 'dir'),
                ),
                3,
                True,
                1,
            ))
    except CalledProcessError as cpe:
        pass

    assert [
        call(
            'pwd',
            check=True,
            cwd='dir',
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=1),
        call(
            'foo',
            check=True,
            cwd='dir',
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=1),
        call(
            'ls',
            check=True,
            cwd='dir',
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=1)
    ] == mock_run.mock_calls
