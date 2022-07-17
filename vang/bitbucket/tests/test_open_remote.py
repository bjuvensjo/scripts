from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.open_remote import do_open_remote, open_remote
from vang.bitbucket.open_remote import parse_args


@pytest.mark.parametrize(
    "git_dir, repo, project, expected",
    [
        (
            ".",
            None,
            None,
            [
                call(
                    [
                        "open",
                        "".join(
                            [
                                "base_url/projects/project_key/repos/repo_slug/commits?",
                                "until=refs%2Fheads%2Fdevelop&merges=include",
                            ]
                        ),
                    ]
                )
            ],
        ),
        (
            ".",
            "project_key/repo_slug",
            None,
            [call(["open", "base_url/projects/project_key/repos/repo_slug/browse"])],
        ),
        (
            ".",
            None,
            "project_key",
            [call(["open", "base_url/projects/project_key"])],
        ),
    ],
)
@patch("vang.bitbucket.open_remote.run", autospec=True)
@patch("vang.bitbucket.open_remote.get_branch", autospec=True)
@patch("vang.bitbucket.open_remote.get_project_and_repo", autospec=True)
def test_do_open_remote(
    mock_get_project_and_repo,
    mock_get_branch,
    mock_run,
    git_dir,
    repo,
    project,
    expected,
):
    mock_get_project_and_repo.return_value = ("project_key", "repo_slug")
    mock_get_branch.return_value = "develop"

    do_open_remote(git_dir, repo, project, "base_url")
    assert mock_run.mock_calls == expected


@pytest.mark.parametrize(
    "repo_dir, repo, project, baseurl, expected",
    [
        (
            ".",
            None,
            None,
            "baseurl",
            [call("abspath", None, None, "baseurl")],
        ),
        (
            ".",
            "project_key/repo_slug",
            None,
            "baseurl",
            [call("abspath", "project_key/repo_slug", None, "baseurl")],
        ),
        (
            ".",
            None,
            "project_key",
            "baseurl",
            [call("abspath", None, "project_key", "baseurl")],
        ),
    ],
)
@patch("vang.bitbucket.open_remote.abspath", autospec=True)
@patch("vang.bitbucket.open_remote.do_open_remote", autospec=True)
def test_open_remote(
    mock_do_open_remote,
    mock_abspath,
    repo_dir,
    repo,
    project,
    baseurl,
    expected,
):
    mock_abspath.return_value = "abspath"
    open_remote(repo_dir, repo, project, baseurl)
    assert mock_do_open_remote.mock_calls == expected
    assert mock_abspath.mock_calls == [call("./.git")]


@pytest.mark.parametrize(
    "args",
    [
        "1-d d -r r",
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
            "",
            {
                "repo_dir": ".",
                "repo": None,
                "project": None,
                "baseurl": "url",
            },
        ],
        [
            "-d d",
            {
                "repo_dir": "d",
                "repo": None,
                "project": None,
                "baseurl": "url",
            },
        ],
        [
            "-r r",
            {
                "repo_dir": ".",
                "repo": "r",
                "project": None,
                "baseurl": "url",
            },
        ],
        [
            "-p p",
            {
                "repo_dir": ".",
                "repo": None,
                "project": "p",
                "baseurl": "url",
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    with patch("vang.bitbucket.open_remote.environ", {"BITBUCKET_REST_URL": "url"}):
        assert parse_args(args.split(" ") if args else "").__dict__ == expected
