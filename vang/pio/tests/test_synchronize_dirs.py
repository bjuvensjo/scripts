from pytest import raises

from unittest.mock import call, patch

from vang.pio.synchronize_dirs import add
from vang.pio.synchronize_dirs import delete
from vang.pio.synchronize_dirs import parse_args
from vang.pio.synchronize_dirs import synchronize_dirs

import pytest


@pytest.fixture
def walk_from():
    return [
        ("/root/source_dir", (".git", "both"), ("source_file", "both")),
        ("/root/source_dir/.git", (), ("source_file",)),
        ("/root/source_dir/both", (), ("source_file", "diff")),
    ]


@pytest.fixture
def walk_to():
    return [
        ("/root/dest_dir", (".git", "both", "dest_dir"), ("dest_file", "both")),
        ("/root/dest_dir/.git", (), ("dest_file",)),
        ("/root/dest_dir/both", (), ("dest_file", "both")),
        ("/root/dest_dir/dest_dir", (), ("dest_file",)),
    ]


@patch("vang.pio.synchronize_dirs.print")
@patch("vang.pio.synchronize_dirs.copyfile", autospec=True)
@patch("vang.pio.synchronize_dirs.cmp", autospec=True)
@patch("vang.pio.synchronize_dirs.exists", autospec=True)
@patch("vang.pio.synchronize_dirs.makedirs", autospec=True)
@patch("vang.pio.synchronize_dirs.walk", autospec=True)
def test_add(
    mock_walk,
    mock_makedirs,
    mock_exists,
    mock_cmp,
    mock_copyfile,
    mock_print,
    walk_from,
):
    mock_walk.return_value = walk_from
    mock_exists.side_effect = lambda x: not x.endswith("source_file")
    mock_cmp.side_effect = lambda x, y: not x.endswith("diff")

    assert add("/root/dest_dir", ["/.git"], "/root/source_dir") == [
        "Added from /root/source_dir/source_file to /root/dest_dir/source_file",
        "Added from /root/source_dir/both/source_file to "
        "/root/dest_dir/both/source_file",
        "Updated from /root/source_dir/both/diff to /root/dest_dir/both/diff",
    ]

    assert mock_makedirs.mock_calls == [
        call("/root/dest_dir", exist_ok=True),
        call("/root/dest_dir/both", exist_ok=True),
    ]

    assert mock_copyfile.mock_calls == [
        call("/root/source_dir/source_file", "/root/dest_dir/source_file"),
        call("/root/source_dir/both/source_file", "/root/dest_dir/both/source_file"),
        call("/root/source_dir/both/diff", "/root/dest_dir/both/diff"),
    ]


@patch("vang.pio.synchronize_dirs.print")
@patch("vang.pio.synchronize_dirs.remove", autospec=True)
@patch("vang.pio.synchronize_dirs.rmtree", autospec=True)
@patch("vang.pio.synchronize_dirs.exists", autospec=True)
@patch("vang.pio.synchronize_dirs.walk", autospec=True)
def test_delete(
    mock_walk,
    mock_exists,
    mock_rmtree,
    mock_remove,
    mock_print,
    walk_to,
):
    mock_walk.return_value = walk_to
    mock_exists.side_effect = lambda x: not (
        x.endswith("dest_file") or "/dest_dir" in x
    )

    assert delete("/root/dest_dir", ["/.git"], "/root/source_dir") == [
        "Removed file /root/dest_dir/dest_file",
        "Removed file /root/dest_dir/both/dest_file",
        "Removed dir /root/dest_dir/dest_dir",
    ]

    assert mock_rmtree.mock_calls == [call("/root/dest_dir/dest_dir")]

    assert mock_remove.mock_calls == [
        call("/root/dest_dir/dest_file"),
        call("/root/dest_dir/both/dest_file"),
    ]


@patch("vang.pio.synchronize_dirs.delete", autospec=True)
@patch("vang.pio.synchronize_dirs.add", autospec=True)
def test_synchronize_dirs(mock_add, mock_delete):
    mock_add.return_value = ["a1", "a2"]
    mock_delete.return_value = ["d1", "d2"]
    assert synchronize_dirs("root/dest_dir", ["/.git"], "/root/source_dir") == [
        "a1",
        "a2",
        "d1",
        "d2",
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1",
        "1 2 3",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "source_dir dest_dir",
            {
                "source_dir": "source_dir",
                "dest_dir": "dest_dir",
                "ignore_sub_paths": ["/.git"],
            },
        ],
        [
            "source_dir dest_dir -i /foo /bar",
            {
                "source_dir": "source_dir",
                "dest_dir": "dest_dir",
                "ignore_sub_paths": ["/foo", "/bar"],
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected
