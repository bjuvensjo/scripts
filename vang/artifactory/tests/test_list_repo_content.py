from unittest.mock import patch, call

import pytest
from pytest import raises

from vang.artifactory.list_repo_content import (
    do_list_repo_content,
    list_repo_content,
    parse_args,
)


@patch("vang.artifactory.list_repo_content.get_repo_content")
def test_do_list_repo_content(mock_get_repo_content):
    repo_content = {
        "files": [{"uri": "f1", "folder": False}, {"uri": "d1", "folder": True}]
    }
    mock_get_repo_content.return_value = repo_content
    assert do_list_repo_content("repo_key") == ["f1"]
    assert do_list_repo_content("repo_key", False) == repo_content["files"]
    mock_get_repo_content.assert_called_with("repo_key")


@patch("vang.artifactory.list_repo_content.print")
@patch("vang.artifactory.list_repo_content.do_list_repo_content")
def test_list_repo_content(mock_list_repo_content, mock_print):
    mock_list_repo_content.return_value = ["f1", "f2"]
    list_repo_content("repo_key", True)
    assert mock_print.mock_calls == [call("f1"), call("f2")]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "k1",
            {
                "repo_key": "k1",
                "only_files": False,
            },
        ],
        [
            "k1 -f",
            {
                "repo_key": "k1",
                "only_files": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
