from multiprocessing.dummy import Process
from unittest.mock import Mock, call, patch

import pytest
from vang.azdo.clone_repos import clone_repos, parse_args


@pytest.mark.parametrize(
    "args, run_commands_expected, print_expected",
    [
        (
            "-o myorg",
            [
                call(
                    [
                        ("git clone https://myorg@myazure/myorg/p1/_git/r1 p1/r1", "."),
                        ("git clone https://myorg@myazure/myorg/p1/_git/r2 p1/r2", "."),
                    ],
                    max_processes=5,
                    timeout=180,
                    check=False,
                )
            ],
            [
                call("01", "01 Cloning into...", end=""),
                call("02", "02 Cloning into...", end=""),
                call("p1/r1"),
                call("p1/r2"),
            ],
        ),
        (
            "-o myorg -b mybranch -d mydir -f",
            [
                call(
                    [
                        (
                            "git clone https://myorg@myazure/myorg/p1/_git/r1 -b mybranch",
                            "mydir",
                        ),
                        (
                            "git clone https://myorg@myazure/myorg/p1/_git/r2 -b mybranch",
                            "mydir",
                        ),
                    ],
                    max_processes=5,
                    timeout=180,
                    check=False,
                )
            ],
            [
                call("01", "01 Cloning into...", end=""),
                call("02", "02 Cloning into...", end=""),
                call("r1"),
                call("r2"),
            ],
        ),
        (
            "-p myorg/p1",
            [
                call(
                    [
                        ("git clone https://myorg@myazure/myorg/p1/_git/r1 p1/r1", "."),
                        ("git clone https://myorg@myazure/myorg/p1/_git/r2 p1/r2", "."),
                    ],
                    max_processes=5,
                    timeout=180,
                    check=False,
                )
            ],
            [
                call("01", "01 Cloning into...", end=""),
                call("02", "02 Cloning into...", end=""),
                call("p1/r1"),
                call("p1/r2"),
            ],
        ),
        (
            "-r myorg/p1/r1 myorg/p1/r2",
            [
                call(
                    [
                        ("git clone https://myorg@myazure/myorg/p1/_git/r1 p1/r1", "."),
                        ("git clone https://myorg@myazure/myorg/p1/_git/r2 p1/r2", "."),
                    ],
                    max_processes=5,
                    timeout=180,
                    check=False,
                )
            ],
            [
                call("01", "01 Cloning into...", end=""),
                call("02", "02 Cloning into...", end=""),
                call("p1/r1"),
                call("p1/r2"),
            ],
        ),
    ],
)
@patch("vang.azdo.clone_repos.print")
@patch("vang.azdo.clone_repos.run_commands")
@patch("vang.azdo.clone_repos.do_list_repos")
@patch("vang.azdo.clone_repos.do_list_projects")
def test_clone_repos(
    mock_do_list_projects,
    mock_do_list_repos,
    mock_run_commands,
    mock_print,
    args,
    run_commands_expected,
    print_expected,
):
    mock_do_list_projects.return_value = ["myorg/p1"]  # Only used parts of response
    mock_do_list_repos.return_value = {
        "value": [
            {
                "name": "r1",
                "remoteUrl": "https://myorg@myazure/myorg/p1/_git/r1",
                "project": {"name": "p1"},
            },
            {
                "name": "r2",
                "remoteUrl": "https://myorg@myazure/myorg/p1/_git/r2",
                "project": {"name": "p1"},
            },
        ]
    }  # Only used parts of response

    mock_run_commands.return_value = [
        Mock(Process, stdout=r.encode("utf-8"))
        for r in ["01 Cloning into...", "02 Cloning into..."]
    ]
    argv = f"dummy -au https://myazure -t mytoken --no-verify_certificate {args}".strip().split(
        " "
    )
    clone_repos(**parse_args(argv[1:]).__dict__)
    assert mock_run_commands.mock_calls == run_commands_expected
    assert mock_print.mock_calls == print_expected
