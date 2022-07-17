from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.create_from_template import commit_all
from vang.tfs.create_from_template import create_and_push_to_dest_repo
from vang.tfs.create_from_template import create_from_template
from vang.tfs.create_from_template import parse_args
from vang.tfs.create_from_template import setup as c_setup
from vang.tfs.create_from_template import update


@patch("vang.tfs.create_from_template.run_command", autospec=True)
@patch(
    "vang.tfs.create_from_template.do_clone_repos",
    return_value=[("clone_url", "repo_dir")],
    autospec=True,
)
def test_setup(mock_do_clone_repos, mock_run_command):
    assert c_setup(
        "repo",
        "branch",
        "dest_repo",
        "dest_branch",
        "work_dir",
    ) == ("clone_url", "work_dir/dest_repo")
    assert mock_do_clone_repos.mock_calls == [
        call("work_dir", branch="branch", repos=["repo"]),
    ]
    assert mock_run_command.mock_calls == [
        call("mv repo_dir work_dir/dest_repo"),
        call("rm -rf .git", cwd="work_dir/dest_repo", return_output=True),
        call("git init", cwd="work_dir/dest_repo", return_output=True),
        call(
            "git checkout -b dest_branch",
            cwd="work_dir/dest_repo",
            return_output=True,
        ),
    ]


@patch("vang.tfs.create_from_template.run_command", autospec=True)
def test_commit_all(mock_run_command):
    commit_all("repo_dir")
    assert mock_run_command.mock_calls == [
        call("git add --all", cwd="repo_dir", return_output=True),
        call(
            'git commit -m "Initial commit"',
            cwd="repo_dir",
            return_output=True,
        ),
    ]


@patch(
    "vang.tfs.create_from_template.get_replace_function",
    return_value="f",
    autospec=True,
)
@patch("vang.tfs.create_from_template.rsr", autospec=True)
def test_update(mock_rsr, mock_get_replace_function):
    update([("old1", "new1"), ("old2", "new2")], "dest_repo_dir")
    mock_rsr.assert_has_calls(
        [
            call("old1", "new1", ["dest_repo_dir"], "f"),
            call("Old1", "New1", ["dest_repo_dir"], "f"),
            call("OLD1", "NEW1", ["dest_repo_dir"], "f"),
            call("old2", "new2", ["dest_repo_dir"], "f"),
            call("Old2", "New2", ["dest_repo_dir"], "f"),
            call("OLD2", "NEW2", ["dest_repo_dir"], "f"),
        ],
        any_order=True,
    )


@patch(
    "vang.tfs.create_from_template.do_create_repo",
    return_value={"remoteUrl": "dest_repo_origin"},
    autospec=True,
)
@patch("vang.tfs.create_from_template.run_command", autospec=True)
def test_create_and_push_to_dest_repo(mock_run_command, mock_create_repo):
    assert (
        create_and_push_to_dest_repo(
            "branch",
            "dest_repo",
            "dest_repo_dir",
        )
        == "dest_repo_origin"
    )
    assert mock_create_repo.mock_calls == [call("dest_repo")]
    assert mock_run_command.mock_calls == [
        call(
            "git remote add origin dest_repo_origin",
            cwd="dest_repo_dir",
            return_output=True,
        ),
        call("git push -u origin branch", cwd="dest_repo_dir", return_output=True),
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1",
        "1, 2, 3",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "src_repo dest_repo",
            {
                "src_branch": "develop",
                "dest_branch": "develop",
                "dest_repo": "dest_repo",
                "src_repo": "src_repo",
                "work_dir": ".",
                "replacements": [],
            },
        ],
        [
            "src_repo dest_repo -sb sb -db db -d d -r old1 new1 old2 new2",
            {
                "src_branch": "sb",
                "dest_branch": "db",
                "dest_repo": "dest_repo",
                "src_repo": "src_repo",
                "work_dir": "d",
                "replacements": ["old1", "new1", "old2", "new2"],
            },
        ],
    ],
)
def test_parse_args(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected


@patch(
    "vang.tfs.create_from_template.setup",
    return_value=("clone_url", "dest_repo_dir"),
    autospec=True,
)
@patch("vang.tfs.create_from_template.update", autospec=True)
@patch("vang.tfs.create_from_template.commit_all", autospec=True)
@patch(
    "vang.tfs.create_from_template.create_and_push_to_dest_repo",
    return_value="dest_repo_origin",
    autospec=True,
)
@patch("vang.tfs.create_from_template.print")
def test_create_from_template(
    mock_print,
    mock_create_and_push_to_dest_repo,
    mock_commit_all,
    mock_update,
    mock_setup,
):
    create_from_template(
        "src_repo",
        "branch",
        "dest_repo",
        "dest_branch",
        "work_dir",
        ["old1", "new1", "old2", "new2"],
    )
    assert mock_setup.mock_calls == [
        call("src_repo", "branch", "dest_repo", "dest_branch", "work_dir"),
    ]
    assert mock_update.mock_calls == [
        call([("old1", "new1"), ("old2", "new2")], "dest_repo_dir"),
    ]
    assert mock_commit_all.mock_calls == [
        call("dest_repo_dir"),
    ]
    assert mock_create_and_push_to_dest_repo.mock_calls == [
        call("dest_branch", "dest_repo", "dest_repo_dir"),
    ]
    assert mock_print.mock_calls == [
        call("Created", "dest_repo_origin"),
    ]
