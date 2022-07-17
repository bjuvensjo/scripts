from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.fork_repos import fork_repo
from vang.bitbucket.fork_repos import do_fork_repos
from vang.bitbucket.fork_repos import fork_repos
from vang.bitbucket.fork_repos import parse_args


@patch("vang.bitbucket.fork_repos.call")
def test_fork_repo(mock_call):
    mock_call.return_value = '"response"'
    assert fork_repo(("project_key", "repo_slug"), "fork_project_key") == (
        ("project_key", "repo_slug"),
        '"response"',
    )
    assert mock_call.mock_calls == [
        call(
            "/rest/api/1.0/projects/project_key/repos/repo_slug",
            {"slug": "repo_slug", "project": {"key": "fork_project_key"}},
            "POST",
        )
    ]


@patch("vang.bitbucket.fork_repos.fork_repo")
def test_do_fork_repos(mock_fork_repo):
    mock_fork_repo.side_effect = lambda x, y: (x, "response")
    assert do_fork_repos(
        [["project_key", "repo_slug"], ["project_key", "repo_slug"]],
        "fork_project_key",
    ) == [
        (["project_key", "repo_slug"], "response"),
        (["project_key", "repo_slug"], "response"),
    ]


@patch("vang.bitbucket.fork_repos.print")
@patch("vang.bitbucket.fork_repos.do_fork_repos")
@patch("vang.bitbucket.fork_repos.get_repo_specs")
def test_fork_repos(mock_get_repo_specs, mock_do_fork_repos, mock_print):
    mock_get_repo_specs.return_value = [("d1", "r1"), ("d2", "r2")]
    mock_do_fork_repos.return_value = [
        (("d1", "r1"), "response1"),
        (("d2", "r2"), "response2"),
    ]
    fork_repos(
        "fork_project_key",
        ["d1", "d2"],
        None,
        None,
    )
    assert mock_get_repo_specs.mock_calls == [call(["d1", "d2"], None, None)]
    assert mock_do_fork_repos.mock_calls == [
        call([("d1", "r1"), ("d2", "r2")], "fork_project_key"),
    ]
    assert mock_print.mock_calls == [call("d1/r1: response1"), call("d2/r2: response2")]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2",
        "1 -d d -r r",
        "1 -d d -p p",
        "1 -r r -p p",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "fork_project_key -d d1 d2",
            {
                "fork_project": "fork_project_key",
                "dirs": ["d1", "d2"],
                "repos": None,
                "projects": None,
            },
        ],
        [
            "fork_project_key -r key1/repo1 key2/repo2",
            {
                "fork_project": "fork_project_key",
                "dirs": ["."],
                "repos": ["key1/repo1", "key2/repo2"],
                "projects": None,
            },
        ],
        [
            "fork_project_key -p key1 key2",
            {
                "fork_project": "fork_project_key",
                "dirs": ["."],
                "repos": None,
                "projects": ["key1", "key2"],
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
