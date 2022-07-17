from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.create_repo import do_create_repo
from vang.bitbucket.create_repo import create_repo
from vang.bitbucket.create_repo import parse_args


@patch("vang.bitbucket.create_repo.call")
def test_do_create_repo(mock_call):
    do_create_repo("project", "repo")
    assert mock_call.mock_calls == [
        call(
            "/rest/api/1.0/projects/project/repos",
            {"name": "repo", "scmId": "git", "forkable": True},
            "POST",
        )
    ]


@patch(
    "vang.bitbucket.create_repo.do_create_repo",
    return_value={"links": {"clone": [{"href": "clone_url"}]}},
)
@patch("builtins.print")
def test_create_repo(mock_print, mock_create_repo):
    assert not create_repo("project", "repo")
    with patch("vang.bitbucket.create_repo.name", "posix"):
        assert mock_print.mock_calls == [
            call(
                "If you already have code ready to be pushed to this "
                "repository then run this in your terminal."
            ),
            call("    git remote add origin clone_url\n    git push -u origin develop"),
            call("(The commands are copied to the clipboard)"),
        ]
    mock_print.reset_mock()
    with patch("vang.bitbucket.create_repo.name", "not-posix"):
        create_repo("project", "repo")
        assert mock_print.mock_calls == [
            call(
                "If you already have code ready to be pushed to this "
                "repository then run this in your terminal."
            ),
            call("    git remote add origin clone_url\n    git push -u origin develop"),
        ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "foo bar baz",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["project repo", {"project": "project", "repository": "repo"}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
