from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.set_default_branches import set_default_branches
from vang.bitbucket.set_default_branches import parse_args
from vang.bitbucket.set_default_branches import set_default_branch
from vang.bitbucket.set_default_branches import set_repo_default_branch


@pytest.fixture
def call_fixtures():
    return 204


@patch("vang.bitbucket.set_default_branches.call")
def test_set_repo_default_branch(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures
    assert set_repo_default_branch(["project_key", "repo_slug"], "develop") == (
        ["project_key", "repo_slug"],
        204,
    )
    assert mock_call.mock_calls == [
        call(
            "/rest/api/1.0/projects/project_key/repos/repo_slug/branches/default",
            {"id": "refs/heads/develop"},
            method="PUT",
            only_response_code=True,
        )
    ]


@patch("vang.bitbucket.set_default_branches.call")
def test_set_default_branch(mock_call, call_fixtures):
    mock_call.return_value = call_fixtures
    assert (
        set_default_branch([["project_key", "repo_slug"]] * 2, "develop")
        == [(["project_key", "repo_slug"], 204)] * 2
    )


@patch("vang.bitbucket.set_default_branches.print")
@patch("vang.bitbucket.set_default_branches.get_repo_specs")
@patch("vang.bitbucket.set_default_branches.call")
def test_set_default_branches(mock_call, mock_get_repo_specs, mock_print, call_fixtures):
    mock_call.return_value = call_fixtures
    mock_get_repo_specs.return_value = [["project_key", "repo_slug"]] * 2
    set_default_branches("develop", ["."], None, ["project_key"] * 2)
    assert mock_print.mock_calls == [call("project_key/repo_slug: 204")] * 2
    assert mock_get_repo_specs.mock_calls == [
        call(["."], None, ["project_key", "project_key"])
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2",
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
        [
            "b",
            {
                "branch": "b",
                "dirs": ["."],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -d d1 d2",
            {
                "branch": "b",
                "dirs": ["d1", "d2"],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -p p1 p2",
            {
                "branch": "b",
                "dirs": ["."],
                "projects": ["p1", "p2"],
                "repos": None,
            },
        ],
        [
            "b -r p/r1 p/r2",
            {
                "branch": "b",
                "dirs": ["."],
                "projects": None,
                "repos": ["p/r1", "p/r2"],
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
