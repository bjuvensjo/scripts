from unittest.mock import MagicMock, call, mock_open, patch

from pytest import raises

from vang.pio.rsr import _in
from vang.pio.rsr import _replace_in_file
from vang.pio.rsr import _replace_file
from vang.pio.rsr import _rsr
from vang.pio.rsr import get_replace_function
from vang.pio.rsr import rsr
from vang.pio.rsr import parse_args

import pytest


def test_get_replace_function():
    assert get_replace_function(False)("Hello.World", ".", "#") == "Hello#World"
    assert get_replace_function(True)("Hello.World", ".", "#") == "###########"


@patch("vang.pio.rsr.remove")
@patch("vang.pio.rsr.replace")
def test__replace_in_file(mock_replace, mock_remove):
    with patch("vang.pio.rsr.open", mock_open(), create=True) as m:
        old_file = MagicMock()
        old_file.__enter__.return_value.__iter__.return_value = [
            "\n".join(["foo.bar"] * 10)
        ]
        old_file.__exit__.return_value = False
        new_file = MagicMock()
        new_file.__exit__.return_value = False
        m.side_effect = (old_file, new_file)

        _replace_in_file(".", "#", "path", get_replace_function(True))
        assert mock_replace.mock_calls == [call("path.tmp", "path")]
        assert mock_remove.mock_calls == []
        assert m.mock_calls == [
            call("path", "tr", encoding="UTF-8", errors="ignore"),
            call("path.tmp", "tw", encoding="UTF-8"),
        ]
        assert new_file.mock_calls == [
            call.__enter__(),
            call.__enter__().write(
                "#######\n#######\n#######\n#######\n#######\n"
                "#######\n#######\n#######\n#######\n#######"
            ),
            call.__exit__(None, None, None),
        ]


@pytest.mark.parametrize(
    "file, expected",
    [
        ("foox", [call("path/foox", "path/barx")]),
        ("baz", []),
    ],
)
@patch("vang.pio.rsr.rename")
def test__replace_file(mock_rename, file, expected):
    _replace_file("foo", "bar", "path", file, get_replace_function(False))
    assert mock_rename.mock_calls == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("foo", True),
        ("bar", True),
        (".o.", True),
        ("baz", False),
        (".o", False),
    ],
)
def test__in(name, expected):
    assert _in(name, ["foo", "bar"]) == expected


@patch("vang.pio.rsr.walk", autospec=True)
@patch("vang.pio.rsr._replace_in_file", autospec=True)
@patch("vang.pio.rsr._replace_file", autospec=True)
def test__rsr(mock__replace_file, mock__replace_in_file, mock_walk):
    mock_walk.return_value = [
        ("/old", ("older", ".git"), ("baz", ".gitignore")),
        ("/old/older", (), ("oldest", "eggs")),
        ("/old/.git", (), ("oldest", "eggs")),
    ]

    def replace_function(x, y, z):
        pass

    _rsr(
        "root",
        [".git", ".gitignore", "target"],
        "old",
        "new",
        replace_function,
    )

    assert mock_walk.mock_calls == [call("root", False)]

    assert mock__replace_file.mock_calls == [
        call("old", "new", "/old", "baz", replace_function),
        call("old", "new", "/old", "older", replace_function),
        call("old", "new", "/old/older", "oldest", replace_function),
        call("old", "new", "/old/older", "eggs", replace_function),
    ]

    assert mock__replace_in_file.mock_calls == [
        call("old", "new", "/old/baz", replace_function),
        call("old", "new", "/old/older/oldest", replace_function),
        call("old", "new", "/old/older/eggs", replace_function),
    ]


@patch("vang.pio.rsr.get_replace_function", autospec=True)
@patch("vang.pio.rsr._rsr", autospec=True)
def test_rsr(mock__rsr, mock_get_replace_function):
    mock_get_replace_function.return_value = "rf"

    rsr("old", "new", ["d1", "d2"], True)

    assert mock_get_replace_function.mock_calls == [call(True)]
    assert mock__rsr.mock_calls == [
        call("d1", [".git", ".gitignore", "target"], "old", "new", "rf"),
        call("d2", [".git", ".gitignore", "target"], "old", "new", "rf"),
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2 3",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["old new", {"old": "old", "new": "new", "dirs": ["."], "regexp": False}],
        [
            "old new -d d1 d2 -r",
            {"old": "old", "new": "new", "dirs": ["d1", "d2"], "regexp": True},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected
