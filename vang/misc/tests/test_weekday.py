from pytest import raises
from unittest.mock import call, patch

from vang.misc.weekday import weekday
from vang.misc.weekday import name
from vang.misc.weekday import parse_args
from vang.misc.weekday import zeller

import pytest


def test_name():
    assert [name(d) for d in [1, 4, 4, 7, 2, 5, 7, 3, 6, 1, 4, 6]] == [
        "monday",
        "thursday",
        "thursday",
        "sunday",
        "tuesday",
        "friday",
        "sunday",
        "wednesday",
        "saturday",
        "monday",
        "thursday",
        "saturday",
    ]


def test_zeller():
    assert [zeller(2018, m, 1) for m in range(1, 13)] == [
        1,
        4,
        4,
        7,
        2,
        5,
        7,
        3,
        6,
        1,
        4,
        6,
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1",
        "1 2",
        "1 2 3 4",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "2018 11 23",
            {
                "year": "2018",
                "month": "11",
                "day": "23",
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


@patch("vang.misc.weekday.print")
def test_weekday(mock_print):
    weekday("2018", "11", "23")
    assert mock_print.mock_calls == [call("friday")]
