from unittest.mock import patch, call

import pytest
from pytest import raises

from vang.jenkins.delete_jobs import do_delete_jobs
from vang.jenkins.delete_jobs import delete_jobs
from vang.jenkins.delete_jobs import parse_args


@patch("vang.jenkins.delete_jobs.call", autospec=True)
def test_do_delete_jobs(mock_call):
    mock_call.return_value = 201

    assert do_delete_jobs(["j1", "j2"]) == [("j1", 201), ("j2", 201)]


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


@patch("vang.jenkins.delete_jobs.print")
@patch("vang.jenkins.delete_jobs.do_delete_jobs", autospec=True)
def test_delete_jobs(mock_do_delete_jobs, mock_print):
    mock_do_delete_jobs.return_value = [("j1", 201), ("j2", 201)]

    delete_jobs(["j1", "j2"])
    assert mock_do_delete_jobs.mock_calls == [call(["j1", "j2"])]
    assert mock_print.mock_calls == [call("j1", 201), call("j2", 201)]
