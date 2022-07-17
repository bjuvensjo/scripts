from unittest.mock import MagicMock, call, mock_open, patch

import pytest
from more_itertools import take
from pytest import raises
from vang.bitbucket.clone_repos import (
    clone,
    clone_repos,
    get_config_commands,
    get_projects_commands,
    get_repos_commands,
    parse_args,
    should_be_cloned,
)


@patch("vang.bitbucket.clone_repos.is_included", return_value=True)
def test_should_be_cloned(mock_is_included):
    mock_has_branch_map = MagicMock(return_value=True)
    assert should_be_cloned(
        "project",
        "repo",
        {"includes": ["includes"], "excludes": ["excludes"]},
        mock_has_branch_map,
    )
    assert mock_is_included.mock_calls == [call("repo", ["excludes"], ["includes"])]


@patch("vang.bitbucket.clone_repos.run_commands", return_value=iter([1, 2, 3]))
@patch("vang.bitbucket.clone_repos.makedirs")
def test_clone(mock_makedirs, mock_run_commands):
    assert take(3, clone(["commands"], "root_dir")) == [1, 2, 3]
    assert mock_makedirs.mock_calls == [call("root_dir", exist_ok=True)]
    assert mock_run_commands.mock_calls == [
        call([("commands", "root_dir")], check=False, max_processes=25, timeout=60)
    ]


@patch(
    "vang.bitbucket.clone_repos.do_get_clone_urls",
    return_value=[
        [
            "clone_dir",
            "project",
            "repo",
            "command",
        ]
    ],
)
def test_get_projects_commands(mock_do_get_clone_urls):
    assert list(get_projects_commands("projects", "branch")) == [
        ("clone_dir", "project", "repo", "command")
    ]
    assert mock_do_get_clone_urls.mock_calls == [
        call("projects", True, "branch", False)
    ]


@patch("builtins.print")
@patch(
    "vang.bitbucket.clone_repos.do_get_clone_urls",
    return_value=[
        ["clone_dir", "project", "repo1", "command"],
        ["clone_dir", "project", "repo2", "command"],
    ],
)
def test_get_repos_commands(mock_do_get_clone_urls, mock_print):
    assert get_repos_commands(
        [
            "project/repo1",
            "project/repo2",
            "project/non_existing_repo",
        ],
        "branch",
    ) == [
        ("clone_dir", "project", "repo1", "command"),
        ("clone_dir", "project", "repo2", "command"),
    ]
    assert mock_do_get_clone_urls.mock_calls == [
        call({"project"}, True, "branch", False)
    ]
    assert mock_print.mock_calls == [
        call("Warning! Non existing repo: project/non_existing_repo")
    ]


@patch("vang.bitbucket.clone_repos.should_be_cloned", return_value=True)
@patch(
    "vang.bitbucket.clone_repos.do_get_clone_urls",
    return_value=[
        ["clone_dir", "project", "repo1", "command"],
        ["clone_dir", "project", "repo2", "command"],
    ],
)
@patch(
    "vang.bitbucket.clone_repos.has_branch",
    return_value=[[("project", "repo1"), True], [("project", "repo2"), False]],
)
def test_get_config_commands(
    mock_has_branch, mock_do_get_clone_urls, mock_should_be_cloned
):
    assert list(
        get_config_commands({"projects": {"project": "project"}, "branch": "branch"})
    ) == [
        ("clone_dir", "project", "repo1", "command"),
        ("clone_dir", "project", "repo2", "command"),
    ]
    assert mock_has_branch.mock_calls == [
        call([("project", "repo1"), ("project", "repo2")], "branch")
    ]
    assert mock_do_get_clone_urls.mock_calls == [
        call(
            {"project": "project"},
            True,
            "branch",
            False,
        )
    ]
    assert mock_should_be_cloned.mock_calls == [
        call(
            "project",
            "repo1",
            "project",
            {("project", "repo1"): True, ("project", "repo2"): False},
        ),
        call(
            "project",
            "repo2",
            "project",
            {("project", "repo1"): True, ("project", "repo2"): False},
        ),
    ]


@patch("builtins.open")
@patch("builtins.print")
@patch("vang.bitbucket.clone_repos.clone")
@patch("vang.bitbucket.clone_repos.get_config_commands")
@patch("vang.bitbucket.clone_repos.get_projects_commands")
@patch("vang.bitbucket.clone_repos.get_repos_commands")
@patch("vang.bitbucket.clone_repos.load")
def test_clone_repos(
    mock_load,
    mock_get_repos_commands,
    mock_get_projects_commands,
    mock_get_config_commands,
    mock_clone,
    mock_print,
    mock_open,
):
    mock_load.return_value = "load"
    mock_process = MagicMock()
    mock_process.stdout.decode.return_value = "Cloned..."
    mock_clone.return_value = [mock_process]
    commands = [
        ["clone_dir", "project", "repo1", "command"],
        ["clone_dir", "project", "repo2", "command"],
    ]
    mock_get_config_commands.return_value = commands
    mock_get_projects_commands.return_value = commands
    mock_get_repos_commands.return_value = commands

    assert not clone_repos("root_dir", projects=["project"], branch="branch")
    assert mock_get_projects_commands.mock_calls == [
        call(
            ["project"],
            "branch",
            False,
        )
    ]
    assert mock_clone.mock_calls == [call(["command", "command"], "root_dir")]
    assert mock_print.mock_calls == [call("01", "Cloned...", end="")]

    assert not clone_repos("root_dir", repos=["repos"], branch="branch")
    assert mock_get_repos_commands.mock_calls == [
        call(
            ["repos"],
            "branch",
            False,
        )
    ]

    assert not clone_repos("root_dir", config="config", branch="branch")
    assert mock_open.mock_calls == [
        call("config", "rt", encoding="utf-8"),
        call().__enter__(),
        call().__exit__(None, None, None),
    ]
    assert mock_get_config_commands.mock_calls == [
        call(
            "load",
            "branch",
            False,
        )
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "foo",
        "-p p -r r",
        "-p p -c c",
        "-r r -c c",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "-p p1 p2",
            {
                "branch": None,
                "config": None,
                "root_dir": ".",
                "flat": False,
                "projects": ["p1", "p2"],
                "repos": None,
            },
        ],
        [
            "-r r1 r2",
            {
                "branch": None,
                "config": None,
                "root_dir": ".",
                "flat": False,
                "projects": None,
                "repos": ["r1", "r2"],
            },
        ],
        [
            "-c c",
            {
                "branch": None,
                "config": "c",
                "root_dir": ".",
                "flat": False,
                "projects": None,
                "repos": None,
            },
        ],
        [
            "-c c -b b -d d -f",
            {
                "branch": "b",
                "config": "c",
                "root_dir": "d",
                "flat": True,
                "projects": None,
                "repos": None,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


# #########################


@pytest.fixture
def clone_urls_fixture():
    return [
        ("clone_dir", "p1", "r1", "git clone http://myorgn/stash/scm/p1/r1.git"),
        ("clone_dir", "p2", "r1", "git clone http://myorgn/stash/scm/p2/r1.git"),
        ("clone_dir", "p2", "r2", "git clone http://myorgn/stash/scm/p2/r2.git"),
    ]


@patch("vang.bitbucket.clone_repos.run_commands")
@patch("vang.bitbucket.clone_repos.do_get_clone_urls")
@patch("vang.bitbucket.clone_repos.makedirs")
def test_clone_repos_projects(
    mock_makedirs,
    mock_do_get_clone_urls,
    mock_run_commands,
    clone_urls_fixture,
):
    mock_do_get_clone_urls.return_value = clone_urls_fixture
    argv = "dummy -p p1 p2".split(" ")
    clone_repos(**parse_args(argv[1:]).__dict__)
    assert mock_makedirs.mock_calls == [call(".", exist_ok=True)]
    assert mock_run_commands.mock_calls[0] == call(
        [
            ("git clone http://myorgn/stash/scm/p1/r1.git", "."),
            ("git clone http://myorgn/stash/scm/p2/r1.git", "."),
            ("git clone http://myorgn/stash/scm/p2/r2.git", "."),
        ],
        max_processes=25,
        timeout=60,
        check=False,
    )


@patch("vang.bitbucket.clone_repos.run_commands")
@patch("vang.bitbucket.clone_repos.do_get_clone_urls")
@patch("vang.bitbucket.clone_repos.makedirs")
def test_clone_repos_repos(
    mock_makedirs,
    mock_do_get_clone_urls,
    mock_run_commands,
    clone_urls_fixture,
):
    mock_do_get_clone_urls.return_value = clone_urls_fixture
    argv = "dummy -r p1/r1 p2/r1".split(" ")
    clone_repos(**parse_args(argv[1:]).__dict__)
    assert mock_makedirs.mock_calls == [call(".", exist_ok=True)]
    assert mock_run_commands.mock_calls[0] == call(
        [
            ("git clone http://myorgn/stash/scm/p1/r1.git", "."),
            ("git clone http://myorgn/stash/scm/p2/r1.git", "."),
        ],
        max_processes=25,
        timeout=60,
        check=False,
    )


@patch("vang.bitbucket.clone_repos.run_commands")
@patch("vang.bitbucket.clone_repos.has_branch")
@patch("vang.bitbucket.clone_repos.do_get_clone_urls")
@patch("vang.bitbucket.clone_repos.makedirs")
def test_clone_repos_config(
    mock_makedirs,
    mock_do_get_clone_urls,
    mock_has_branch,
    mock_run_commands,
    clone_urls_fixture,
):
    mock_do_get_clone_urls.return_value = clone_urls_fixture
    mock_has_branch.return_value = [
        (("p1", "r1"), True),
        (("p2", "r1"), True),
        (("p2", "r2"), True),
    ]
    argv = "dummy -c c".split(" ")
    config = """{
        "branch": "develop",
        "projects": {
            "p1": {
                "includes": [
                ],
                "excludes": [
                ]
            },
            "p2": {
                "includes": [
                    ".*1.*"
                ],
                "excludes": [
                ]
            }
        }
        }
    """
    with patch("builtins.open", mock_open(read_data=config)):
        clone_repos(**parse_args(argv[1:]).__dict__)
    assert mock_makedirs.mock_calls == [call(".", exist_ok=True)]
    assert mock_run_commands.mock_calls[0] == call(
        [
            ("git clone http://myorgn/stash/scm/p1/r1.git", "."),
            ("git clone http://myorgn/stash/scm/p2/r1.git", "."),
        ],
        max_processes=25,
        timeout=60,
        check=False,
    )
