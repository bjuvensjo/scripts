from os.path import dirname
from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.maven.reactor_summary import get_failures
from vang.maven.reactor_summary import get_project
from vang.maven.reactor_summary import get_reactor_summary
from vang.maven.reactor_summary import get_successes
from vang.maven.reactor_summary import get_summary
from vang.maven.reactor_summary import reactor_summary
from vang.maven.reactor_summary import parse_args
from vang.maven.reactor_summary import print_summary


@pytest.fixture
def reactor_summary_fixture():
    return [
        "[INFO] myorg:app 0.0.1-SNAPSHOT ................. SUCCESS [ 1.095 s]",
        "[INFO] yorg:app 0.0.1-SNAPSHOT ................. FAILURE [ 1.095 s]",
        "[INFO] config 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]",
        "[INFO] foofig 1.0.0-SNAPSHOT ................. SKIPPED [  4.300 s]",
    ]


def test_get_reactor_summary():
    with open(dirname(__file__) + "/mvn.log", "rt", encoding="utf-8") as f:
        mvn_log = f.readlines()
        assert get_reactor_summary(mvn_log) == [
            "[INFO] myorg:app 0.0.1-SNAPSHOT ................. SUCCESS [ 1.095 s]",
            "[INFO] config 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]",
        ]


@pytest.mark.parametrize(
    "mvn_log, expected",
    [
        (
            [
                "[INFO] Building myorg:app 1.0.0-SNAPSHOT",
                "[INFO] ----------------------------------------------------------",
                "[INFO] BUILD SUCCESS",
                "[INFO] ----------------------------------------------------------",
                "[INFO] Total time: 50.316 s",
            ],
            ["[INFO] myorg:app 1.0.0-SNAPSHOT SUCCESS"],
        ),
        (
            [
                "[INFO] Building myorg:app 1.0.0-SNAPSHOT",
                "[INFO] ----------------------------------------------------------",
                "[INFO] BUILD FAILURE",
                "[INFO] ----------------------------------------------------------",
                "[INFO] Total time: 50.316 s",
            ],
            ["[INFO] myorg:app 1.0.0-SNAPSHOT FAILURE"],
        ),
    ],
)
def test_get_reactor_summary_single_project(mvn_log, expected):
    assert get_reactor_summary(mvn_log) == expected


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            "[INFO] myorg:app 0.0.1-SNAPSHOT ................. SUCCESS [ 1.095 s]",
            "myorg:app",
        ),
        (
            "[INFO] config 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]",
            "config",
        ),
    ],
)
def test_get_project(line, expected):
    assert get_project(line) == expected


@pytest.mark.parametrize(
    "expected",
    [
        (["myorg:app", "config"]),
    ],
)
def test_get_successes(reactor_summary_fixture, expected):
    assert get_successes(reactor_summary_fixture) == expected


@pytest.mark.parametrize(
    "expected",
    [
        (["yorg:app", "foofig"]),
    ],
)
def test_get_failures(reactor_summary_fixture, expected):
    assert get_failures(reactor_summary_fixture) == expected


@patch("vang.maven.reactor_summary.print_summary")
def test_get_summary(mock_print_summary):
    assert get_summary([dirname(__file__) + "/mvn.log"] * 2, True) == (
        [
            "myorg:app",
            "config",
            "myorg:app",
            "config",
        ],
        [],
    )
    assert mock_print_summary.mock_calls == [
        call(
            ["myorg:app", "config", "myorg:app", "config"],
            [],
        )
    ]


@patch("vang.maven.reactor_summary.print")
def test_print_summary(mock_print):
    print_summary(
        ["myorg:app", "config", "myorg:app", "config"],
        ["yorg:app"],
    )
    assert mock_print.mock_calls == [
        call(
            "\n".join(
                [
                    "********************************************************************************",
                    "*********************************** Summary ************************************",
                    "********************************************************************************",
                    "config...................................................................SUCCESS",
                    "config...................................................................SUCCESS",
                    "myorg:app................................................................SUCCESS",
                    "myorg:app................................................................SUCCESS",
                    "yorg:app.................................................................FAILURE",
                    "********************************************************************************",
                ]
            )
        )
    ]


@patch("vang.maven.reactor_summary.glob")
@patch("vang.maven.reactor_summary.realpath")
@patch("vang.maven.reactor_summary.print_summary")
@patch("vang.maven.reactor_summary.get_summary")
def test_reactor_summary(
    mock_get_summary, mock_print_summary, mock_realpath, mock_glob
):
    mock_get_summary.return_value = [["success"], ["failure"]]
    mock_realpath.side_effect = lambda x: x
    mock_glob.return_value = ["p1", "p2"]
    reactor_summary(["r1", "r2"], "mvn.log")

    assert mock_get_summary.mock_calls == [call(["p1", "p2", "p1", "p2"])]
    assert mock_glob.mock_calls == [
        call("r1/**/mvn.log", recursive=True),
        call(
            "r2/**/mvn.log",
            recursive=True,
        ),
    ]
    assert mock_print_summary.mock_calls == [call(["success"], ["failure"])]


@pytest.mark.parametrize(
    "args",
    [
        "foo",
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
            {"roots": ["."], "log_file_name": "mvn.log"},
        ],
        [
            "-d d1 d2 -l l",
            {"roots": ["d1", "d2"], "log_file_name": "l"},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
