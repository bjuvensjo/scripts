from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.has_branch import has_branch
from vang.bitbucket.has_branch import main
from vang.bitbucket.has_branch import parse_args


@pytest.fixture
def branches_fixture():
    return [
        (
            ("project_key", "repo_slug"),
            [
                {
                    "id": "refs/heads/develop",
                    "displayId": "develop",
                    "type": "BRANCH",
                    "latestCommit": "c92880a67728af1101c0dc776a30b57b5fedd497",
                    "latestChangeset": "c92880a67728af1101c0dc776a30b57b5fedd497",
                    "isDefault": True,
                }
            ],
        ),
    ]


@patch("vang.bitbucket.has_branch.do_get_branches")
def test_has_branch(mock_call, branches_fixture):
    mock_call.return_value = branches_fixture
    assert (
        list(has_branch([["project_key", "repo_slug"]] * 2, "develop"))
        == [(["project_key", "repo_slug"], True)] * 2
    )
    assert (
        list(has_branch([["project_key", "repo_slug"]] * 2, "not_develop"))
        == [(["project_key", "repo_slug"], False)] * 2
    )


@pytest.mark.parametrize(
    "branch, only_has, only_not_has, expected",
    [
        (
            "develop",
            False,
            False,
            [
                call("project_key/repo_slug, develop: True"),
                call("project_key/repo_slug, develop: True"),
            ],
        ),
        (
            "develop",
            True,
            False,
            [call("project_key/repo_slug"), call("project_key/repo_slug")],
        ),
        (
            "not_develop",
            False,
            True,
            [call("project_key/repo_slug"), call("project_key/repo_slug")],
        ),
    ],
)
@patch("vang.bitbucket.has_branch.print")
@patch("vang.bitbucket.has_branch.get_repo_specs")
@patch("vang.bitbucket.has_branch.do_get_branches")
def test_main(
    mock_do_get_branches,
    mock_get_repo_specs,
    mock_print,
    branch,
    only_has,
    only_not_has,
    expected,
    branches_fixture,
):
    mock_do_get_branches.return_value = branches_fixture
    mock_get_repo_specs.return_value = [("project_key", "repo_slug")] * 2
    main(branch, only_has, only_not_has, projects=["project_key"])
    assert mock_get_repo_specs.mock_calls == [call(None, None, ["project_key"])]
    assert mock_print.mock_calls == expected


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2",
        "1 -o -n",
        "1 -d -r",
        "1 -d -p",
        "1 -r -p",
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
                "only_has": False,
                "only_not_has": False,
                "dirs": ["."],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -o",
            {
                "branch": "b",
                "only_has": True,
                "only_not_has": False,
                "dirs": ["."],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -n",
            {
                "branch": "b",
                "only_has": False,
                "only_not_has": True,
                "dirs": ["."],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -d d1 d2",
            {
                "branch": "b",
                "only_has": False,
                "only_not_has": False,
                "dirs": ["d1", "d2"],
                "projects": None,
                "repos": None,
            },
        ],
        [
            "b -p p1 p2",
            {
                "branch": "b",
                "only_has": False,
                "only_not_has": False,
                "dirs": ["."],
                "projects": ["p1", "p2"],
                "repos": None,
            },
        ],
        [
            "b -r p/r1 p/r2",
            {
                "branch": "b",
                "only_has": False,
                "only_not_has": False,
                "dirs": ["."],
                "projects": None,
                "repos": ["p/r1", "p/r2"],
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
