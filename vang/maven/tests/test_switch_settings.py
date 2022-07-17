from os import environ
from unittest.mock import call, patch

from pytest import raises

from vang.maven.switch_settings import switch_settings
from vang.maven.switch_settings import parse_args
from vang.maven.switch_settings import do_switch_settings

import pytest


@patch("vang.maven.switch_settings.exists", autospec=True, side_effect=(False, True))
@patch("vang.maven.switch_settings.run_command", autospec=True, return_value=(0, ""))
def test_do_switch_settings(mock_run_command, mock_exists):
    with raises(ValueError):
        do_switch_settings("not_exists")
    assert do_switch_settings("exists") == (0, "")

    home = environ["HOME"]
    assert mock_exists.mock_calls == [
        call(f"{home}/.m2/settings_not_exists.xml"),
        call(f"{home}/.m2/settings_exists.xml"),
    ]
    assert mock_run_command.mock_calls == [
        call(f"ln -sf {home}/.m2/settings_exists.xml {home}/.m2/settings.xml", True)
    ]


@pytest.mark.parametrize(
    "name, switch_setting_calls, print_calls",
    [
        (
            "posix",
            [call("project")],
            [call("")],
        ),
        (
            "not posix",
            [],
            [
                call(
                    "Platform not supported. "
                    "Please implement, and make a pull request."
                )
            ],
        ),
    ],
)
@patch("vang.maven.switch_settings.print")
@patch(
    "vang.maven.switch_settings.do_switch_settings", return_value=(0, ""), autospec=True
)
def test_switch_settings(
    mock_do_switch_settings, mock_print, name, switch_setting_calls, print_calls
):
    with patch("vang.maven.switch_settings.name", name):
        switch_settings("project")
        assert mock_do_switch_settings.mock_calls == switch_setting_calls
        assert mock_print.mock_calls == print_calls


@pytest.mark.parametrize(
    "args",
    [
        "",
        "foo bar",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "project",
            {"ending": "project"},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
