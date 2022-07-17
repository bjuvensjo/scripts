from unittest.mock import patch, call

import pytest
from pytest import raises

from vang.git.open_remote import get_origin_remote_url, do_open_remote, parse_args


@pytest.mark.parametrize(
    "remote, expected",
    [
        ("origin", "https://github.com/origin/scripts.git"),
        ("foo", "https://github.com/foo/scripts.git"),
        ("none", None),
    ],
)
@patch("vang.git.open_remote.run_command")
def test_get_origin_remote_url(mock_command, remote, expected):
    mock_command.return_value = (
        0,
        "\n".join(
            (
                "origin	https://github.com/origin/scripts.git (fetch)",
                "origin	https://github.com/origin/scripts.git (push)",
                "foo	https://github.com/foo/scripts.git (fetch)",
                "foo	https://github.com/foo/scripts.git (push)",
            )
        ),
    )
    assert get_origin_remote_url("repo_dir", remote) == expected


@pytest.mark.parametrize(
    "remote_url, expected",
    [
        (
            "https://github.com/origin/scripts.git",
            [call(["open", "https://github.com/origin/scripts.git"])],
        ),
        (None, []),
    ],
)
@patch("vang.git.open_remote.run")
@patch("vang.git.open_remote.get_origin_remote_url")
def test_do_open_remote(mock_get_origin_remote_url, mock_run, remote_url, expected):
    mock_get_origin_remote_url.return_value = remote_url
    do_open_remote("repo_dir", "origin")
    assert mock_run.mock_calls == expected


@pytest.mark.parametrize(
    "args",
    [
        "foo",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["", {"repo_dir": ".", "remote": "origin"}],
        ["-d repo_dir -r remote", {"repo_dir": "repo_dir", "remote": "remote"}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
