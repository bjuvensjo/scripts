from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.get_tags import get_all_tags
from vang.bitbucket.get_tags import do_get_tags
from vang.bitbucket.get_tags import get_tags
from vang.bitbucket.get_tags import parse_args


@pytest.fixture
def fixtures():
    return [
        {
            "id": f"refs/tags/t{n}",
            "displayId": f"t{n}",
            "type": "TAG",
            "latestCommit": "f89ed59",
            "latestChangeset": "f89ed5",
            "hash": "430f79",
        }
        for n in range(50)
    ]


@patch("vang.bitbucket.get_tags.get_all")
def test_get_all_tags(mock_get_all, fixtures):
    mock_get_all.return_value = fixtures
    assert list(get_all_tags(["project_key", "repo_slug"], "")) == [
        (
            ["project_key", "repo_slug"],
            {
                "displayId": f"t{n}",
                "hash": "430f79",
                "id": f"refs/tags/t{n}",
                "latestChangeset": "f89ed5",
                "latestCommit": "f89ed59",
                "type": "TAG",
            },
        )
        for n in range(50)
    ]


@pytest.fixture
def tags_fixture():
    return [
        (
            ["project_key", "repo_slug"],
            {
                "id": "refs/tags/t",
                "displayId": "t",
                "type": "TAG",
                "latestCommit": "f89ed59695b89280c474d6c20f6c026dee7eca06",
                "latestChangeset": "f89ed59695b89280c474d6c20f6c026dee7eca06",
                "hash": "430f7929b4eac0e553d2594435dda49a7149c8e2",
            },
        )
    ]


@patch("vang.bitbucket.get_tags.get_all_tags")
def test_do_get_tags(mock_get_all_tags, tags_fixture):
    mock_get_all_tags.return_value = tags_fixture
    assert (
        list(
            do_get_tags(
                [
                    ["project_key", "repo_slug"],
                    ["project_key", "repo_slug"],
                ],
                "",
            )
        )
        == [tags_fixture[0]] * 2
    )


@pytest.mark.parametrize(
    "name, print_calls",
    [
        (True, [call("t")]),
        (False, [call("project_key/repo_slug: t")]),
    ],
)
@patch("vang.bitbucket.get_tags.print")
@patch("vang.bitbucket.get_tags.do_get_tags")
@patch("vang.bitbucket.get_tags.get_repo_specs")
def test_get_tags(
    mock_get_repo_specs,
    mock_do_get_tags,
    mock_print,
    name,
    print_calls,
    tags_fixture,
):
    mock_get_repo_specs.return_value = [["project_key", "repo_slug"]]
    mock_do_get_tags.return_value = tags_fixture
    get_tags(name=name, dirs=["."])
    assert mock_get_repo_specs.mock_calls == [call(["."], None, None)]
    assert mock_do_get_tags.mock_calls == [call([["project_key", "repo_slug"]], "")]
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
                "tag": "",
                "dirs": ["."],
                "name": False,
                "projects": None,
                "repos": None,
            },
        ],
        [
            "-t t -n -d d1 d2",
            {
                "tag": "t",
                "dirs": ["d1", "d2"],
                "name": True,
                "projects": None,
                "repos": None,
            },
        ],
        [
            "-t t -n -r p/r1 p/r2",
            {
                "tag": "t",
                "dirs": ["."],
                "name": True,
                "projects": None,
                "repos": ["p/r1", "p/r2"],
            },
        ],
        [
            "-t t -n -p p1 p2",
            {
                "tag": "t",
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
