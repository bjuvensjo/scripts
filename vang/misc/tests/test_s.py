from unittest.mock import call, patch

from pytest import raises

from vang.misc.s import get_cases
from vang.misc.s import get_split
from vang.misc.s import get_zipped_cases
from vang.misc.s import main
from vang.misc.s import parse_args

import pytest


@pytest.mark.parametrize(
    "s, expected",
    [
        ("fooBarBaz", ["foo", "Bar", "Baz"]),
        ("foo_Bar_Baz", ["foo", "Bar", "Baz"]),
        ("foo-Bar-Baz", ["foo", "Bar", "Baz"]),
    ],
)
def test_get_split(s, expected):
    assert get_split(s) == expected


@pytest.mark.parametrize(
    "s",
    [
        ("radioButton"),
        ("RadioButton"),
        ("radio_button"),
        ("RADIO_BUTTON"),
        ("radio-button"),
        ("RADIO-BUTTON"),
    ],
)
def test_get_cases(s):
    cases = [
        "radioButton",
        "RadioButton",
        "radiobutton",
        "RADIOBUTTON",
        "radio_button",
        "RADIO_BUTTON",
        "radio-button",
        "RADIO-BUTTON",
    ]
    assert get_cases(s) == cases


@pytest.mark.parametrize(
    "strings, expected",
    [
        (
            ["foo"],
            [
                ("foo",),
                ("Foo",),
                ("foo",),
                ("FOO",),
                ("foo",),
                ("FOO",),
                ("foo",),
                ("FOO",),
            ],
        ),
        (
            ["foo", "bar", "baz"],
            [
                ("foo", "bar", "baz"),
                ("Foo", "Bar", "Baz"),
                ("foo", "bar", "baz"),
                ("FOO", "BAR", "BAZ"),
                ("foo", "bar", "baz"),
                ("FOO", "BAR", "BAZ"),
                ("foo", "bar", "baz"),
                ("FOO", "BAR", "BAZ"),
            ],
        ),
    ],
)
def test_zipped_cases(strings, expected):
    assert list(get_zipped_cases(strings)) == expected


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
    "args, expected", [["foo bar baz", {"strings": ["foo", "bar", "baz"]}]]
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


@patch("builtins.print")
def test_main(mock_print):
    main(["foo", "bar"])
    assert mock_print.mock_calls == [
        call("foo bar"),
        call("Foo Bar"),
        call("foo bar"),
        call("FOO BAR"),
        call("foo bar"),
        call("FOO BAR"),
        call("foo bar"),
        call("FOO BAR"),
    ]
