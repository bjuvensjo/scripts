from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_clone_urls_grep import do_get_clone_urls_grep
from vang.bitbucket.get_clone_urls_grep import get_clone_urls_grep
from vang.bitbucket.get_clone_urls_grep import parse_args


@pytest.fixture
def projects_fixture():
    return [
        {
            "key": f"P{n}",
            "id": 1250,
            "name": f"P{n}",
            "public": False,
            "type": "NORMAL",
            "links": {"self": [{"href": f"http://myorg/stash/projects/p{n}"}]},
        }
        for n in range(25)
    ]


@pytest.fixture
def clone_urls_fixture():
    return [(None, "Px", "repo_slug", "http://myorgn/stash/scm/px/repo_slug.git")]


@patch("vang.bitbucket.get_clone_urls_grep.do_get_clone_urls", autospec=True)
@patch("vang.bitbucket.get_clone_urls_grep.do_get_projects", autospec=True)
def test_do_get_clone_urls_grep(
    mock_do_get_projects,
    mock_do_get_clone_urls,
    projects_fixture,
    clone_urls_fixture,
):
    mock_do_get_projects.return_value = projects_fixture
    mock_do_get_clone_urls.return_value = clone_urls_fixture
    assert do_get_clone_urls_grep([".*4", "P2.*"]) == clone_urls_fixture
    assert mock_do_get_projects.mock_calls == [call()]
    assert mock_do_get_clone_urls.mock_calls == [
        call(["P2", "P4", "P14", "P20", "P21", "P22", "P23", "P24"], False)
    ]


@patch("vang.bitbucket.get_clone_urls_grep.print")
@patch("vang.bitbucket.get_clone_urls_grep.do_get_clone_urls_grep", autospec=True)
def test_get_clone_urls_grep(mock_do_get_clone_urls_grep, mock_print, clone_urls_fixture):
    mock_do_get_clone_urls_grep.return_value = clone_urls_fixture
    get_clone_urls_grep([".*"], False)
    assert mock_print.mock_calls == [call("http://myorgn/stash/scm/px/repo_slug.git")]


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
            {
                "patterns": ["p1", "p2"],
                "command": False,
            },
        ],
        [
            "p1 p2 -c",
            {
                "patterns": ["p1", "p2"],
                "command": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
