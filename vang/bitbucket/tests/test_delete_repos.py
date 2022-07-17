from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.delete_repos import delete_repo
from vang.bitbucket.delete_repos import do_delete_repos
from vang.bitbucket.delete_repos import delete_repos
from vang.bitbucket.delete_repos import parse_args


@patch(
    "vang.bitbucket.delete_repos.call",
    return_value={
        "context": None,
        "message": "Repository scheduled for deletion.",
        "exceptionName": None,
    },
)
def test_delete_repo(mock_call):
    assert delete_repo(("project", "repo")) == (
        ("project", "repo"),
        {
            "context": None,
            "exceptionName": None,
            "message": "Repository scheduled for deletion.",
        },
    )
    assert mock_call.mock_calls == [
        call("/rest/api/1.0/projects/project/repos/repo", method="DELETE")
    ]


@patch("vang.bitbucket.delete_repos.delete_repo", return_value=1)
def test_do_delete_repos(mock_delete_repo):
    assert do_delete_repos(
        [
            ("project", "repo1"),
            ("project", "repo2"),
        ]
    ) == [1, 1]
    assert mock_delete_repo.mock_calls == [
        call(("project", "repo1")),
        call(("project", "repo2")),
    ]


@patch("builtins.print")
@patch(
    "vang.bitbucket.delete_repos.do_delete_repos",
    side_effect=[
        [
            [("project", "repo1"), "deleted"],
            [("project", "repo1"), "deleted"],
        ]
    ],
)
@patch(
    "vang.bitbucket.delete_repos.get_repo_specs",
    return_value=[
        ("project", "repo1"),
        ("project", "repo2"),
    ],
)
def test_delete_repos(mock_get_repo_specs, mock_delete_repos, mock_print):
    assert not delete_repos(dirs=None, projects=["project"])
    assert mock_get_repo_specs.mock_calls == [call(None, None, ["project"])]
    assert mock_delete_repos.mock_calls == [
        call(
            [
                ("project", "repo1"),
                ("project", "repo2"),
            ]
        )
    ]
    assert mock_print.mock_calls == [
        call("project/repo1: deleted"),
        call("project/repo1: deleted"),
    ]


@pytest.mark.parametrize(
    "args",
    [
        "foo",
        "-d d -r r",
        "-d d -p p",
        "-r r -p p",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["", {"dirs": ["."], "projects": None, "repos": None}],
        ["-d d", {"dirs": ["d"], "projects": None, "repos": None}],
        ["-r r", {"dirs": ["."], "projects": None, "repos": ["r"]}],
        ["-p p", {"dirs": ["."], "projects": ["p"], "repos": None}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
