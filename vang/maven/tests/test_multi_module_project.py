from unittest.mock import call, mock_open, patch

import pytest
from pytest import raises

from vang.maven.multi_module_project import get_pom
from vang.maven.multi_module_project import get_pom_infos
from vang.maven.multi_module_project import multi_module_project
from vang.maven.multi_module_project import make_project
from vang.maven.multi_module_project import parse_args


@pytest.fixture
def pom_infos_fixture():
    return [
        {
            "pom_path": "/root/m1/pom.xml",
            "artifact_id": "m1",
            "group_id": "com.example",
            "version": "1.0.0-SNAPSHOT",
            "packaging": "jar",
        },
        {
            "pom_path": "/root/m2/pom.xml",
            "artifact_id": "m2",
            "group_id": "com.example",
            "version": "1.0.0-SNAPSHOT",
            "packaging": "jar",
        },
    ]


def test_get_pom(pom_infos_fixture):
    expected = """<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>group_id</groupId>
    <artifactId>artifact_id</artifactId>
    <version>version</version>
    <packaging>pom</packaging>
    <modules>
        <module>../m1</module>
        <module>../m2</module>
    </modules>
</project>"""

    assert (
        get_pom(
            pom_infos_fixture,
            "/root/ws",
            "group_id",
            "artifact_id",
            "version",
        )
        == expected
    )


@patch("vang.maven.multi_module_project.makedirs")
@patch("vang.maven.multi_module_project.get_pom")
def test_make_project(mock_get_pom, mock_makedirs, pom_infos_fixture):
    mock_get_pom.return_value = "pom"
    with patch("vang.maven.multi_module_project.open", mock_open()) as m:
        make_project(
            pom_infos_fixture,
            "/root/ws",
            "group_id",
            "artifact_id",
            "version",
        )
        assert mock_get_pom.mock_calls == [
            call(
                [
                    {
                        "pom_path": "/root/m1/pom.xml",
                        "artifact_id": "m1",
                        "group_id": "com.example",
                        "version": "1.0.0-SNAPSHOT",
                        "packaging": "jar",
                    },
                    {
                        "pom_path": "/root/m2/pom.xml",
                        "artifact_id": "m2",
                        "group_id": "com.example",
                        "version": "1.0.0-SNAPSHOT",
                        "packaging": "jar",
                    },
                ],
                "/root/ws",
                "group_id",
                "artifact_id",
                "version",
            )
        ]
        assert mock_makedirs.mock_calls == [call("/root/ws")]
        assert m.mock_calls == [
            call("/root/ws/pom.xml", "wt", encoding="utf-8"),
            call().__enter__(),
            call().write("pom"),
            call().__exit__(None, None, None),
        ]


@patch("vang.maven.multi_module_project.pom.get_pom_info")
@patch("vang.maven.multi_module_project.pom.get_pom_paths")
def test_get_pom_infos(mock_get_pom_paths, mock_get_pom_info, pom_infos_fixture):
    mock_get_pom_paths.return_value = (
        "/root/m1/pom.xml",
        "/root/m2/pom.xml",
    )
    mock_get_pom_info.side_effect = pom_infos_fixture

    assert get_pom_infos("source_dir") == [
        {
            "artifact_id": "m1",
            "group_id": "com.example",
            "packaging": "jar",
            "pom_path": "/root/m1/pom.xml",
            "version": "1.0.0-SNAPSHOT",
        },
        {
            "artifact_id": "m2",
            "group_id": "com.example",
            "packaging": "jar",
            "pom_path": "/root/m2/pom.xml",
            "version": "1.0.0-SNAPSHOT",
        },
    ]


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
            {"use_defaults": False},
        ],
        [
            "-d",
            {"use_defaults": True},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


@pytest.mark.parametrize(
    "use_defaults, source_dir_expected, expected",
    [
        (
            False,
            [call("s")],
            [
                call(
                    [
                        {
                            "pom_path": "/root/m1/pom.xml",
                            "artifact_id": "m1",
                            "group_id": "com.example",
                            "version": "1.0.0-SNAPSHOT",
                            "packaging": "jar",
                        },
                        {
                            "pom_path": "/root/m2/pom.xml",
                            "artifact_id": "m2",
                            "group_id": "com.example",
                            "version": "1.0.0-SNAPSHOT",
                            "packaging": "jar",
                        },
                    ],
                    "o",
                    "g",
                    "a",
                    "v",
                ),
            ],
        ),
        (
            True,
            [call(".")],
            [
                call(
                    [
                        {
                            "pom_path": "/root/m1/pom.xml",
                            "artifact_id": "m1",
                            "group_id": "com.example",
                            "version": "1.0.0-SNAPSHOT",
                            "packaging": "jar",
                        },
                        {
                            "pom_path": "/root/m2/pom.xml",
                            "artifact_id": "m2",
                            "group_id": "com.example",
                            "version": "1.0.0-SNAPSHOT",
                            "packaging": "jar",
                        },
                    ],
                    artifact_id="ws-tests",
                    group_id="my.group",
                    output_dir="ws-tests",
                    source_dir=".",
                    version="1.0.0-SNAPSHOT",
                )
            ],
        ),
    ],
)
@patch("vang.maven.multi_module_project.getcwd")
@patch("vang.maven.multi_module_project.input")
@patch("vang.maven.multi_module_project.make_project")
@patch("vang.maven.multi_module_project.get_pom_infos")
def test_multi_module_project(
    mock_get_pom_infos,
    mock_make_project,
    mock_input,
    mock_getcwd,
    pom_infos_fixture,
    use_defaults,
    source_dir_expected,
    expected,
):
    mock_getcwd.return_value = "tests"
    mock_get_pom_infos.return_value = pom_infos_fixture
    mock_input.side_effect = ("g", "a", "v", "s", "o")

    multi_module_project(use_defaults)

    assert mock_get_pom_infos.mock_calls == source_dir_expected
    assert mock_make_project.mock_calls == expected
