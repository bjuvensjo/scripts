from unittest.mock import mock_open, patch, call

import pytest
from pytest import raises

from vang.misc.wc import (
    is_excluded,
    is_included,
    count_words,
    count_letters,
    count,
    count_all,
    get_files,
    parse_args,
)


@pytest.mark.parametrize(
    "excluded, expected",
    [
        [("foo.txt",), True],
        [(".*.txt",), True],
        [(".*.txt", "bar.txt"), True],
        [("foo.txtx",), False],
    ],
)
def test_is_excluded(excluded, expected):
    assert is_excluded("foo.txt", excluded) == expected


@pytest.mark.parametrize(
    "included, expected",
    [
        [("foo.txt",), True],
        [(".*.txt",), True],
        [(".*.txt", "bar.txt"), True],
        [("foo.txtx",), False],
    ],
)
def test_is_included(included, expected):
    assert is_included("foo.txt", included) == expected


@patch("vang.misc.wc.walk")
def test_get_files(mock_walk):
    mock_walk.return_value = iter([["root", "dir", ("f1", "f2")]])
    files = list(get_files("root_dir"))
    assert files == [("root", "f1"), ("root", "f2")]


def test_count_words():
    assert count_words(" foo bar baz  ") == 3


def test_count_letters():
    assert count_letters(" foo bar baz  ") == 11


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="Nobody inspects the \n spammish repetition",
)
def test_count(mock_file):
    assert count("root", "file") == (2, 5, 38)
    assert call("root/file", "rt", encoding="utf-8") in mock_file.mock_calls


@patch("vang.misc.wc.get_files")
@patch("vang.misc.wc.count")
def test_count_all(mock_count, mock_get_files):
    mock_get_files.return_value = ("f1", "f2")
    mock_count.return_value = (1, 2, 3)
    assert count_all() == {"files": 2, "letters": 6, "lines": 2, "words": 4}


@pytest.mark.parametrize(
    "args",
    [
        "foo",
        "-x bar",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["", {"dirs": ["."], "excluded": [], "included": [".*"]}],
        [
            "-d d1 d2 -e e1 e2 -i i1 i2",
            {"dirs": ["d1", "d2"], "excluded": ["e1", "e2"], "included": ["i1", "i2"]},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
