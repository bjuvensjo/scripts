from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_branches import do_get_branches
from vang.bitbucket.get_branches import get_branches
from vang.bitbucket.get_branches import parse_args


@pytest.fixture
def branches_fixture():
    return [
        {
            "id": "refs/heads/release",
            "displayId": "release",
            "type": "BRANCH",
            "latestCommit": "f89ed59695b89280c474d6c20f6c026dee7eca06",
            "latestChangeset": "f89ed59695b89280c474d6c20f6c026dee7eca06",
            "isDefault": False,
        },
        {
            "id": "refs/heads/develop",
            "displayId": "develop",
            "type": "BRANCH",
            "latestCommit": "c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767",
            "latestChangeset": "c3e8f3994a2f8c8fc46a5cc0cb5fd766948f7767",
            "isDefault": True,
        },
    ]


@patch("vang.bitbucket.get_branches.get_all")
def test_do_get_branches(mock_get_all, branches_fixture):
    mock_get_all.return_value = branches_fixture
    assert [
        (["project_key", "repo_slug"], branches_fixture),
        (["project_key", "repo_slug"], branches_fixture),
    ] == list(
        do_get_branches(
            [
                ["project_key", "repo_slug"],
                ["project_key", "repo_slug"],
            ],
            "",
        )
    )


@pytest.mark.parametrize(
    "name, print_calls",
    [
        (
            True,
            [
                call("release"),
                call("develop"),
            ],
        ),
        (
            False,
            [
                call("project_key/repo_slug: release"),
                call("project_key/repo_slug: develop"),
            ],
        ),
    ],
)
@patch("vang.bitbucket.get_branches.print")
@patch("vang.bitbucket.get_branches.do_get_branches")
@patch("vang.bitbucket.get_branches.get_repo_specs")
def test_get_branches(
    mock_get_repo_specs,
    mock_do_get_branches,
    mock_print,
    name,
    print_calls,
    branches_fixture,
):
    mock_get_repo_specs.return_value = [["project_key", "repo_slug"]]
    mock_do_get_branches.return_value = [[["project_key", "repo_slug"], branches_fixture]]
    get_branches(name=name, dirs=["."])
    assert mock_get_repo_specs.mock_calls == [call(["."], None, None)]
    assert mock_do_get_branches.mock_calls == [call([["project_key", "repo_slug"]], "")]
    assert mock_print.mock_calls == print_calls


@pytest.mark.parametrize(
    "args",
    [
        "-d d -r r",
        "-d d -p p",
        "-r r -p p",
        "1",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "",
            {
                "branch": "",
                "dirs": ["."],
                "name": False,
                "projects": None,
                "repos": None,
            },
        ],
        [
            "-b b -n -d d1 d2",
            {
                "branch": "b",
                "dirs": ["d1", "d2"],
                "name": True,
                "projects": None,
                "repos": None,
            },
        ],
        [
            "-b b -n -r p/r1 p/r2",
            {
                "branch": "b",
                "dirs": ["."],
                "name": True,
                "projects": None,
                "repos": ["p/r1", "p/r2"],
            },
        ],
        [
            "-b b -n -p p1 p2",
            {
                "branch": "b",
                "dirs": ["."],
                "name": True,
                "projects": ["p1", "p2"],
                "repos": None,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
