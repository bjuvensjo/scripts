from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.get_repos import do_get_repos, get_repos, parse_args


@pytest.mark.parametrize(
    "params, expected",
    [
        (
            {"organisations": ["organisation"]},
            [
                (
                    "organisation/project",
                    {"name": "name", "remoteUrl": "remoteUrl"},
                )
            ],
        ),
        (
            {"projects": ["organisation/project"]},
            [
                (
                    "organisation/project",
                    {"name": "name", "remoteUrl": "remoteUrl"},
                )
            ],
        ),
        ({"projects": ["organisation/project"], "names": True}, ["name"]),
        (
            {"projects": ["organisation/project"], "repo_specs": True},
            ["organisation/project/name"],
        ),
        ({"projects": ["organisation/project"], "urls": True}, ["remoteUrl"]),
    ],
)
@patch("vang.tfs.get_repos.do_get_projects", autospec=True)
@patch("vang.tfs.get_repos.call", autospec=True)
def test_do_get_repos(mock_call, mock_do_get_projects, params, expected):
    mock_call.return_value = {"value": [{"name": "name", "remoteUrl": "remoteUrl"}]}
    mock_do_get_projects.return_value = ["organisation/project"]
    assert do_get_repos() == []
    assert do_get_repos(**params) == expected


@patch("vang.tfs.get_repos.print")
@patch("vang.tfs.get_repos.do_get_repos", autospec=True)
def test_get_repos(mock_do_get_repos, mock_print):
    mock_do_get_repos.return_value = ["repo1", "repo2"]
    get_repos("organisations", "projects", "names", "repo_specs", "urls")
    assert mock_do_get_repos.mock_calls == [
        call("organisations", "projects", "names", "repo_specs", "urls")
    ]
    assert mock_print.mock_calls == [call("repo1"), call("repo2")]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "-o",
        "-p",
        "-o o -p p",
        "-o o -n -r",
        "-o o -n -u",
        "-o o -r -u",
        "-o o -n foo",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "-o o1 o2",
            {
                "names": False,
                "organisations": ["o1", "o2"],
                "projects": None,
                "repo_specs": False,
                "urls": False,
            },
        ],
        [
            "-p o/p1 o/p2",
            {
                "names": False,
                "organisations": None,
                "projects": ["o/p1", "o/p2"],
                "repo_specs": False,
                "urls": False,
            },
        ],
        [
            "-o o -n",
            {
                "names": True,
                "organisations": ["o"],
                "projects": None,
                "repo_specs": False,
                "urls": False,
            },
        ],
        [
            "-o o -r",
            {
                "names": False,
                "organisations": ["o"],
                "projects": None,
                "repo_specs": True,
                "urls": False,
            },
        ],
        [
            "-o o -u",
            {
                "names": False,
                "organisations": ["o"],
                "projects": None,
                "repo_specs": False,
                "urls": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected
