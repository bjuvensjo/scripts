from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.tfs.get_projects import do_get_projects, get_projects, parse_args


def test_do_get_projects():
    assert do_get_projects(None) == []
    assert do_get_projects([]) == []
    with patch(
        "vang.tfs.get_projects.call",
        return_value={
            "count": 1,
            "value": [
                {
                    "id": "id",
                    "name": "project",
                    "revision": 272509,
                    "state": "wellFormed",
                    "url": "remoteUrl",
                    "visibility": "private",
                }
            ],
        },
        autospec=True,
    ):
        assert do_get_projects(["organisation"]) == [
            (
                "organisation",
                {
                    "id": "id",
                    "name": "project",
                    "revision": 272509,
                    "state": "wellFormed",
                    "url": "remoteUrl",
                    "visibility": "private",
                },
            )
        ]
        assert do_get_projects(["organisation"], project_specs=True) == [
            "organisation/project"
        ]
        assert do_get_projects(["organisation"], names=True) == ["project"]
        assert do_get_projects(["organisation"], project_specs=True, names=True) == [
            "project"
        ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "-n n -p -p",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "o1 o2",
            {"names": False, "organisations": ["o1", "o2"], "project_specs": False},
        ],
        ["o1 -n", {"names": True, "organisations": ["o1"], "project_specs": False}],
        ["o1 -p", {"names": False, "organisations": ["o1"], "project_specs": True}],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ")).__dict__ == expected


def test_get_projects():
    with patch(
        "vang.tfs.get_projects.do_get_projects",
        return_value=["project1", "project2"],
        autospec=True,
    ) as mock_do_get_projects:
        with patch("vang.tfs.get_projects.print") as mock_print:
            get_projects("organisations", False, True)
            assert mock_do_get_projects.mock_calls == [call("organisations", False, True)]
            assert mock_print.mock_calls == [call("project1"), call("project2")]
