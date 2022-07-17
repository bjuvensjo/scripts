from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.get_branches import (
    do_get_branches,
    get_repo_branches,
    get_branches,
    parse_args,
)


def test_get_repo_branches():
    with patch(
        "vang.tfs.get_branches.call",
        return_value={
            "value": [
                {
                    "name": "refs/heads/develop",
                    "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                    "url": "remoteUrl",
                    "statuses": [],
                }
            ],
            "count": 1,
        },
        autospec=True,
    ) as mock_call:
        assert get_repo_branches("organisation", "project", "repository") == [
            {
                "name": "refs/heads/develop",
                "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                "url": "remoteUrl",
                "statuses": [],
            }
        ]
        assert mock_call.mock_calls == [
            call(
                "/organisation/project/_apis/git/"
                "repositories/repository/refs/heads?includeStatuses=true"
                "&api-version=3.2"
            )
        ]


def test_do_get_branches():
    assert do_get_branches(None) == []
    assert do_get_branches([]) == []
    with patch(
        "vang.tfs.get_branches.do_get_repos",
        return_value=["organisation/project/repo"],
        autospec=True,
    ) as mock_do_get_repos:
        with patch(
            "vang.tfs.get_branches.get_repo_branches",
            return_value=[
                {
                    "name": "refs/heads/develop",
                    "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                    "url": "remoteUrl",
                    "statuses": [],
                }
            ],
            autospec=True,
        ) as mock_get_repo_branches:
            assert do_get_branches(organisations=["organisation"]) == [
                (
                    "organisation/project/repo",
                    [
                        {
                            "name": "develop",
                            "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                            "statuses": [],
                            "url": "remoteUrl",
                        }
                    ],
                )
            ]
            assert mock_do_get_repos.mock_calls == [
                call(organisations=["organisation"], repo_specs=True)
            ]
            assert mock_get_repo_branches.mock_calls == [
                call("organisation", "project", "repo")
            ]
            mock_do_get_repos.reset_mock()
            mock_get_repo_branches.reset_mock()

            assert do_get_branches(projects=["organisation/project"]) == [
                (
                    "organisation/project/repo",
                    [
                        {
                            "name": "develop",
                            "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                            "statuses": [],
                            "url": "remoteUrl",
                        }
                    ],
                )
            ]
            assert mock_do_get_repos.mock_calls == [
                call(projects=["organisation/project"], repo_specs=True)
            ]
            assert mock_get_repo_branches.mock_calls == [
                call("organisation", "project", "repo")
            ]
            mock_do_get_repos.reset_mock()
            mock_get_repo_branches.reset_mock()

            assert do_get_branches(repos=["organisation/project/repo"]) == [
                (
                    "organisation/project/repo",
                    [
                        {
                            "name": "develop",
                            "objectId": "071bd4a8b19c37b2c5290b127c787f8acd52272e",
                            "statuses": [],
                            "url": "remoteUrl",
                        }
                    ],
                )
            ]
            assert mock_do_get_repos.mock_calls == []
            assert mock_get_repo_branches.mock_calls == [
                call("organisation", "project", "repo")
            ]

            assert do_get_branches(repos=["organisation/project/repo"], names=True) == [
                ("organisation/project/repo", ["develop"]),
            ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "-o o -p -p",
        "-o o -r -r",
        "-p -p -r r",
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
                "repos": None,
            },
        ],
        [
            "-p p1 p2",
            {
                "names": False,
                "organisations": None,
                "projects": ["p1", "p2"],
                "repos": None,
            },
        ],
        [
            "-r r1 r2",
            {
                "names": False,
                "organisations": None,
                "projects": None,
                "repos": ["r1", "r2"],
            },
        ],
        [
            "-o o -n",
            {"names": True, "organisations": ["o"], "projects": None, "repos": None},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected


def test_get_branches():
    with patch(
        "vang.tfs.get_branches.do_get_branches",
        return_value=[["r1", ["b1", "b2"]], ["r2", ["b1", "b2"]]],
        autospec=True,
    ) as mock_do_get_branches:
        with patch("vang.tfs.get_branches.print") as mock_print:
            get_branches("organisations", None, None, False)
            assert mock_do_get_branches.mock_calls == [
                call("organisations", None, None, False)
            ]
            assert mock_print.mock_calls == [
                call("r1: b1"),
                call("r1: b2"),
                call("r2: b1"),
                call("r2: b2"),
            ]
