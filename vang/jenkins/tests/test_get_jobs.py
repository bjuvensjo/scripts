from unittest.mock import patch

import pytest
from pytest import raises

from vang.jenkins.get_jobs import FAILURE
from vang.jenkins.get_jobs import SUCCESS
from vang.jenkins.get_jobs import do_get_jobs, NOT_BUILT, UNKNOWN
from vang.jenkins.get_jobs import map_color
from vang.jenkins.get_jobs import parse_args


def test_map_color():
    assert map_color("blue") == SUCCESS
    assert map_color("notbuilt") == NOT_BUILT
    assert map_color("red") == FAILURE
    assert map_color("") == UNKNOWN
    assert map_color("x") == UNKNOWN


@pytest.mark.parametrize(
    "statuses, only_names, expected",
    [
        (
            [SUCCESS, FAILURE],
            False,
            [
                {"color": "blue", "name": "success"},
                {"color": "red", "name": "failure"},
            ],
        ),
        ([SUCCESS, FAILURE], True, ["success", "failure"]),
        ([SUCCESS], True, ["success"]),
        ([FAILURE], True, ["failure"]),
    ],
)
@patch("vang.jenkins.get_jobs.call", autospec=True)
def test_get_jobs(mock_call, statuses, only_names, expected):
    mock_call.return_value = {
        "jobs": [
            {"name": "success", "color": "blue"},
            {"name": "failure", "color": "red"},
        ]
    }

    assert do_get_jobs(statuses, only_names) == expected


@pytest.mark.parametrize(
    "args",
    [
        "1",
        "-f f -s s",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "",
            {
                "only_failures": False,
                "only_names": False,
                "only_successes": False,
                "only_not_built": False,
                "only_unknown": False,
                "view": None,
            },
        ],
        [
            "-n -f",
            {
                "only_failures": True,
                "only_names": True,
                "only_successes": False,
                "only_not_built": False,
                "only_unknown": False,
                "view": None,
            },
        ],
        [
            "-n -s -v MyView",
            {
                "only_failures": False,
                "only_names": True,
                "only_successes": True,
                "only_not_built": False,
                "only_unknown": False,
                "view": "MyView",
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
