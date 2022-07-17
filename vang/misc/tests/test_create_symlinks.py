from unittest.mock import call, mock_open, patch

import pytest
from pytest import raises

from vang.misc.create_symlinks import create_symlinks
from vang.misc.create_symlinks import has_main
from vang.misc.create_symlinks import is_excluded
from vang.misc.create_symlinks import map_to_link_name
from vang.misc.create_symlinks import parse_args


def test_is_excluded():
    assert is_excluded("__init__.py")
    assert is_excluded("fooslaskbar.py")
    assert is_excluded("fooSlaskbar.py")
    assert not is_excluded("foo.py")


def test_has_main():
    with patch(
        "builtins.open", mock_open(read_data="foo\nif __name__ == '__main__':\nfoo")
    ):
        assert has_main("")

    with patch(
        "builtins.open", mock_open(read_data='foo\nif __name__ == "__main__":\nfoo')
    ):
        assert has_main("")

    with patch("builtins.open", mock_open(read_data="foo\nfoo")):
        assert not has_main("")


def test_map_to_link_name():
    assert (
        map_to_link_name("/git/scripts/vang/bitbucket/clone_repos.py")
        == "bitbucket-clone-repos"
    )


@patch("vang.misc.create_symlinks.makedirs")
@patch(
    "vang.misc.create_symlinks.glob",
    return_value=[
        "/vang/bitbucket/clone_repos.py",
        "/vang/bitbucket/create_from_template.py",
        "/vang/bitbucket/create_repo.py",
    ],
)
@patch("vang.misc.create_symlinks.has_main", return_value=True)
@patch("vang.misc.create_symlinks.is_excluded", return_value=False)
def test_create_symlinks(mock_is_excluded, mock_has_main, mock_glob, mock_makedirs):
    with patch("vang.misc.create_symlinks.exists", return_value=True):
        with patch("builtins.print") as mock_print:
            create_symlinks("source", "target")
            assert mock_print.mock_calls == [
                call("target/bitbucket-clone-repos already exists"),
                call("target/bitbucket-create-from-template already exists"),
                call("target/bitbucket-create-repo already exists"),
            ]
    with patch("vang.misc.create_symlinks.exists", return_value=False):
        with patch("builtins.print") as mock_print:
            with patch("vang.misc.create_symlinks.run_command") as mock_run_command:
                create_symlinks("source", "target")
                assert mock_print.mock_calls == [
                    call(
                        "ln -s /vang/bitbucket/clone_repos.py "
                        "target/bitbucket-clone-repos"
                    ),
                    call(
                        "ln -s /vang/bitbucket/create_from_template.py "
                        "target/bitbucket-create-from-template"
                    ),
                    call(
                        "ln -s /vang/bitbucket/create_repo.py "
                        "target/bitbucket-create-repo"
                    ),
                ]
                assert mock_run_command.mock_calls == [
                    call(
                        "ln -s /vang/bitbucket/clone_repos.py "
                        "target/bitbucket-clone-repos"
                    ),
                    call(
                        "ln -s /vang/bitbucket/create_from_template.py "
                        "target/bitbucket-create-from-template"
                    ),
                    call(
                        "ln -s /vang/bitbucket/create_repo.py "
                        "target/bitbucket-create-repo"
                    ),
                ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "foo",
        "foo bar baz",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        ["source target", {"source": "source", "target": "target"}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
