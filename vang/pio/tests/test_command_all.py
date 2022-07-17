from pathlib import Path
from unittest.mock import MagicMock, call, patch

from pytest import raises

from vang.pio.command_all import command_all, execute_in_parallel
from vang.pio.command_all import execute_in_sequence
from vang.pio.command_all import get_command
from vang.pio.command_all import get_work_dirs
from vang.pio.command_all import main
from vang.pio.command_all import parse_args

import pytest


@patch("vang.pio.command_all.realpath", side_effect=lambda x: x)
@patch(
    "vang.pio.command_all.glob",
    return_value=[
        "root/sub/foo/.git",
        "root/sub/bar/.git",
    ],
)
def test_get_work_dirs(mock_glob, mock_realpath):
    assert get_work_dirs(".git", "root") == [
        Path("root/sub/foo"),
        Path("root/sub/bar"),
    ]


def test_get_command():
    assert get_command([]) == [""]
    assert get_command(["pwd"]) == ["pwd"]
    assert get_command(["pwd", "ls"]) == ["pwd && ls"]


@patch("vang.pio.command_all.run_commands", return_value=iter([1, 2]))
@patch("vang.pio.command_all.get_work_dirs", return_value=["foo", "bar"])
def test_execute_in_parallel(mock_get_work_dirs, mock_run_commands):
    assert list(execute_in_parallel("root", ["pwd", "ls"], find="find")) == [1, 2]
    assert mock_get_work_dirs.mock_calls == [call("find", "root")]
    assert mock_run_commands.mock_calls == [
        call(
            (("pwd && ls", "foo"), ("pwd && ls", "bar")), check=False, max_processes=25
        )
    ]


@patch("vang.pio.command_all.run", side_effect=[1, 2])
@patch("vang.pio.command_all.get_work_dirs", return_value=["foo", "bar"])
def test_execute_in_sequence(mock_get_work_dirs, mock_run):
    assert list(
        execute_in_sequence("root", ["pwd", "ls"], find="find", timeout=10)
    ) == [1, 2]
    assert mock_get_work_dirs.mock_calls == [call("find", "root")]
    assert mock_run.mock_calls == [
        call(
            "pwd && ls",
            check=False,
            cwd="foo",
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=10,
        ),
        call(
            "pwd && ls",
            check=False,
            cwd="bar",
            shell=True,
            stderr=-2,
            stdout=-1,
            timeout=10,
        ),
    ]


@patch("builtins.print")
@patch("vang.pio.command_all.execute_in_parallel")
@patch("vang.pio.command_all.execute_in_sequence")
def test_command_all(mock_execute_in_sequence, mock_execute_in_parallel, mock_print):
    processes = [MagicMock(stdout=b" output   ")]
    mock_execute_in_parallel.return_value = processes
    mock_execute_in_sequence.return_value = processes
    assert not command_all("root", ["pwd", "ls"], find="find", sequence=False)
    assert not command_all("root", ["pwd", "ls"], find="find", sequence=True)
    assert mock_execute_in_parallel.mock_calls == [call("root", ["pwd", "ls"], "find")]
    assert mock_execute_in_sequence.mock_calls == [call("root", ["pwd", "ls"], "find")]
    assert mock_print.mock_calls == [call("output"), call("output")]


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
        [
            "pwd ls",
            {
                "commands": ["pwd", "ls"],
                "find": ".git/",
                "root": ".",
                "sequence": False,
            },
        ],
        [
            "pwd -r root -f find -s",
            {"commands": ["pwd"], "find": "find", "root": "root", "sequence": True},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
