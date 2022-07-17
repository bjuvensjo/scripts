from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_clone_urls import do_get_clone_urls
from vang.bitbucket.get_clone_urls import get_clone_urls
from vang.bitbucket.get_clone_urls import parse_args


@pytest.fixture
def repos_fixture():
    return [
        {
            "slug": f"foo.r{n}",
            "id": 9000 + n,
            "name": f"foo.r{n}",
            "scmId": "git",
            "state": "AVAILABLE",
            "statusMessage": "Available",
            "forkable": True,
            "project": {
                "key": "project_key",
                "id": 1000 + n,
                "name": "project_name",
                "public": False,
                "type": "NORMAL",
                "links": {
                    "self": [{"href": "http://myorg/stash/projects/project_key"}]
                },
            },
            "public": False,
            "links": {
                "clone": [
                    {
                        "href": f"http://myorg/stash/scm/project_key/foo.r{n}.git",
                        "name": "http",
                    }
                ],
                "self": [
                    {
                        "href": f"http://myorg/stash/projects/project_key/repos/foo.r{n}/browse"
                    }
                ],
            },
        }
        for n in range(10)
    ]


@pytest.mark.parametrize(
    "command, branch, flat, expected",
    [
        (
            False,
            False,
            False,
            [
                (
                    None,
                    "project_key",
                    f"foo.r{n}",
                    f"http://myorg/stash/scm/project_key/foo.r{n}.git",
                )
                for n in range(10)
            ],
        ),
        (
            True,
            False,
            False,
            [
                (
                    f"project_key/foo/r{n}",
                    "project_key",
                    f"foo.r{n}",
                    "git clone http://myorg/stash/scm/project_key/"
                    f"foo.r{n}.git project_key/foo/r{n}",
                )
                for n in range(10)
            ],
        ),
        (
            True,
            "develop",
            True,
            [
                (
                    f"project_key/foo.r{n}",
                    "project_key",
                    f"foo.r{n}",
                    "git clone -b develop http://myorg/stash/scm/project_key/"
                    f"foo.r{n}.git project_key/foo.r{n}",
                )
                for n in range(10)
            ],
        ),
    ],
)
@patch("vang.bitbucket.get_clone_urls.get_all_repos", autospec=True)
def test_do_get_clone_urls(
    mock_get_all_repos,
    command,
    branch,
    flat,
    expected,
    repos_fixture,
):
    mock_get_all_repos.return_value = repos_fixture
    assert (
        list(
            do_get_clone_urls(
                ["project_key"] * 2,
                command,
                branch,
                flat,
            )
        )
        == expected
    )
    assert mock_get_all_repos.mock_calls == [
        call(["project_key", "project_key"]),
    ]


@pytest.mark.parametrize(
    "command, branch, flat, expected",
    [
        (
            False,
            False,
            False,
            [
                call(f"http://myorg/stash/scm/project_key/foo.r{n}.git")
                for n in range(10)
            ],
        ),
        (
            True,
            False,
            False,
            [
                call(
                    "git clone http://myorg/stash/scm/project_key/"
                    f"foo.r{n}.git project_key/foo/r{n}"
                )
                for n in range(10)
            ],
        ),
        (
            True,
            "develop",
            True,
            [
                call(
                    "git clone -b develop http://myorg/stash/scm/project_key/"
                    f"foo.r{n}.git project_key/foo.r{n}"
                )
                for n in range(10)
            ],
        ),
    ],
)
@patch("vang.bitbucket.get_clone_urls.print")
@patch("vang.bitbucket.get_clone_urls.get_all_repos", autospec=True)
def test_get_clone_urls(
    mock_get_all_repos,
    mock_print,
    command,
    branch,
    flat,
    expected,
    repos_fixture,
):
    mock_get_all_repos.return_value = repos_fixture
    get_clone_urls(["project_key"] * 2, command, branch, flat)
    assert mock_print.mock_calls == expected


@pytest.mark.parametrize(
    "args",
    [
        "",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else "")


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "p1 p2",
            {"projects": ["p1", "p2"], "command": False, "branch": None, "flat": False},
        ],
        [
            "p1 p2 -c -b develop -f",
            {
                "projects": ["p1", "p2"],
                "command": True,
                "branch": "develop",
                "flat": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
