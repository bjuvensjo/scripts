from unittest.mock import call, patch

from pytest import raises

from vang.misc.basic import get_basic_auth
from vang.misc.basic import get_basic_auth_header
from vang.misc.basic import basic
from vang.misc.basic import parse_args

import pytest


def test_get_basic_auth():
    assert get_basic_auth("username", "password") == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="


def test_get_basic_auth_header():
    assert (
        get_basic_auth_header("username", "password")
        == "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ="
    )


@pytest.mark.parametrize(
    "args",
    [
        "foo",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else "")


@pytest.mark.parametrize(
    "args, expected", [["foo bar", {"password": "bar", "username": "foo"}]]
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else []).__dict__ == expected


def test_basic():
    with patch("vang.misc.basic.name", "posix"), patch(
        "vang.misc.basic.system"
    ) as mock_system, patch("builtins.print") as mock_print:
        basic("username", "password")
        assert mock_system.mock_calls == [
            call("echo 'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=\\c' | pbcopy")
        ]
        assert mock_print.mock_calls == [
            call("'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=' copied to clipboard")
        ]
    with patch("vang.misc.basic.name", "not-posix"), patch(
        "builtins.print"
    ) as mock_print:
        basic("username", "password")
        assert mock_print.mock_calls == [
            call("Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=")
        ]
