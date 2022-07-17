from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.delete_repo import do_delete_repo, delete_repo, parse_args


def test_do_delete_repo():
    first_call_response = {"id": "id"}
    second_call_response = "response"
    with patch(
        "vang.tfs.delete_repo.call",
        side_effect=[first_call_response, second_call_response],
        autospec=True,
    ) as mock_call:
        assert do_delete_repo("org/project/name") == second_call_response
        assert mock_call.mock_calls == [
            call(
                "/org/project/_apis/git/repositories/name?api-version=3.2", method="GET"
            ),
            call(
                "/org/project/_apis/git/repositories/id?api-version=3.2",
                method="DELETE",
                only_response_code=True,
            ),
        ]


def test_delete_repo():
    with patch(
        "vang.tfs.delete_repo.do_delete_repo", return_value="response", autospec=True
    ) as mock_do_delete_repo:
        with patch("vang.tfs.delete_repo.print") as mock_print:
            delete_repo("repo")
            assert mock_do_delete_repo.mock_calls == [call("repo")]
            assert mock_print.mock_calls == [call("response")]


@pytest.mark.parametrize("args", ["", "foo bar"])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "organisation/project/repo",
            {"repo": "organisation/project/repo"},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected
