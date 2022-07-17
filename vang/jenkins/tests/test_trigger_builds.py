from unittest.mock import patch, call

from pytest import raises

from vang.jenkins.trigger_builds import do_trigger_builds
from vang.jenkins.trigger_builds import trigger_builds
from vang.jenkins.trigger_builds import parse_args

import pytest


@patch("vang.jenkins.trigger_builds.call", autospec=True)
def test_do_trigger_builds(mock_call):
    mock_call.return_value = 201

    assert do_trigger_builds(["j1", "j2"]) == [("j1", 201), ("j2", 201)]
    assert mock_call.mock_calls == [
        call("/job/j1/build", method="POST", only_response_code=True),
        call("/job/j2/build", method="POST", only_response_code=True),
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["j1 j2", {"job_names": ["j1", "j2"]}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


@patch("vang.jenkins.trigger_builds.print")
@patch("vang.jenkins.trigger_builds.do_trigger_builds", autospec=True)
def test_trigger_builds(mock_do_trigger_builds, mock_print):
    mock_do_trigger_builds.return_value = [("j1", 201), ("j2", 201)]

    trigger_builds(["j1", "j2"])
    assert mock_do_trigger_builds.mock_calls == [call(["j1", "j2"])]
    assert mock_print.mock_calls == [call("j1", 201), call("j2", 201)]
