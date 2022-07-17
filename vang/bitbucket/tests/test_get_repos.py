from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_repos import get_all_repos
from vang.bitbucket.get_repos import do_get_repos
from vang.bitbucket.get_repos import get_repos
from vang.bitbucket.get_repos import parse_args


def get_all_fixtures(start, end):
    return [
        {
            "slug": f"r{n}",
            "id": 9000 + n,
            "name": f"r{n}",
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
                        "href": f"http://myorg/stash/scm/project_key/r{n}.git",
                        "name": "http",
                    }
                ],
                "self": [
                    {
                        "href": f"http://myorg/stash/projects/project_key/repos/r{n}/browse"
                    }
                ],
            },
        }
        for n in range(start, end)
    ]


@pytest.fixture
def fixtures():
    return get_all_fixtures(0, 30)


@pytest.mark.parametrize(
    "only_name, only_spec, expected",
    [
        (False, False, [v for v in get_all_fixtures(0, 30)]),
        (True, False, [f"r{n}" for n in range(30)]),
        (False, True, [("project_key", f"r{n}") for n in range(30)]),
    ],
)
@patch("vang.bitbucket.get_repos.get_all", autospec=True)
def test_do_get_repos(mock_get_all, only_name, only_spec, expected, fixtures):
    mock_get_all.return_value = fixtures
    assert list(do_get_repos("project_key", only_name, only_spec)) == expected


@patch("vang.bitbucket.get_repos.do_get_repos", autospec=True)
def test_get_all_repos(mock_do_get_repos):
    mock_do_get_repos.return_value = ["r"]
    assert list(get_all_repos(["p1", "p2"])) == ["r", "r"]
    assert mock_do_get_repos.mock_calls == [
        call("p1", False, False),
        call("p2", False, False),
    ]


@pytest.mark.parametrize(
    "only_name, only_spec, expected",
    [
        (False, False, [call(v) for v in get_all_fixtures(0, 30)]),
        (True, False, [call(f"r{n}") for n in range(30)]),
        (False, True, [call(f"project_key/r{n}") for n in range(30)]),
    ],
)
@patch("vang.bitbucket.get_repos.print")
@patch("vang.bitbucket.get_repos.get_all", autospec=True)
def test_get_repos(mock_get_all, mock_print, only_name, only_spec, expected, fixtures):
    mock_get_all.return_value = fixtures
    get_repos(["project_key"], only_name, only_spec)
    assert mock_print.mock_calls == expected


@pytest.mark.parametrize(
    "args",
    [
        "",
        "-n",
        "-r",
        "1 -n -r",
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
            {
                "projects": ["p1", "p2"],
                "name": False,
                "repo_specs": False,
            },
        ],
        [
            "p1 p2 -n",
            {
                "projects": ["p1", "p2"],
                "name": True,
                "repo_specs": False,
            },
        ],
        [
            "p1 p2 -r",
            {
                "projects": ["p1", "p2"],
                "name": False,
                "repo_specs": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
