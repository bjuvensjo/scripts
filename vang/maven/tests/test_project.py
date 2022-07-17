from unittest.mock import call, patch

import pytest

from vang.maven.project import get_pom
from vang.maven.project import project
from vang.maven.project import make_dirs
from vang.maven.project import make_project


def test_get_pom():
    expected = """<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
        http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>group_id</groupId>
    <artifactId>artifact_id</artifactId>
    <version>version</version>
    <name>${project.groupId}:${project.artifactId}</name>
    <description>${project.artifactId}</description>
    <packaging>packaging</packaging>
    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>${maven.compiler.source}</source>
                    <target>${maven.compiler.target}</target>
                    <compilerId>groovy-eclipse-compiler</compilerId>
                </configuration>
                <dependencies>
                    <dependency>
                        <groupId>org.codehaus.groovy</groupId>
                        <artifactId>groovy-eclipse-compiler</artifactId>
                        <version>3.7.0</version>
                    </dependency>
                    <!-- for 2.8.0-01 and later you must have an explicit dependency on groovy-eclipse-batch -->
                    <dependency>
                        <groupId>org.codehaus.groovy</groupId>
                        <artifactId>groovy-eclipse-batch</artifactId>
                        <version>3.0.8-01</version>
                    </dependency>
                </dependencies>
            </plugin>
        </plugins>
    </build>
    <dependencies>
        <dependency>
            <groupId>org.codehaus.groovy</groupId>
            <artifactId>groovy</artifactId>
            <version>3.0.8</version>
        </dependency>
    </dependencies>   
</project>
"""
    print(get_pom("1.8", "group_id", "artifact_id", "version", "packaging"))
    assert get_pom("1.8", "group_id", "artifact_id", "version", "packaging") == expected


@pytest.mark.parametrize(
    "packaging, expected",
    [
        (
            "jar",
            [
                call("output_dir"),
                call("output_dir/src/main/java/group_id/artifact_id"),
                call("output_dir/src/main/resources/group_id/artifact_id"),
                call("output_dir/src/test/java/group_id/artifact_id"),
                call("output_dir/src/test/resources/group_id/artifact_id"),
            ],
        ),
        (
            "war",
            [
                call("output_dir"),
                call("output_dir/src/main/java/group_id/artifact_id"),
                call("output_dir/src/main/resources/group_id/artifact_id"),
                call("output_dir/src/test/java/group_id/artifact_id"),
                call("output_dir/src/test/resources/group_id/artifact_id"),
                call("output_dir/src/main/webapp"),
            ],
        ),
    ],
)
def test_make_dirs(packaging, expected):
    with patch("vang.maven.project.makedirs") as mock_makedirs:
        make_dirs("output_dir", "group_id", "artifact_id", packaging)
        assert mock_makedirs.mock_calls == expected


def test_make_project():
    with patch("vang.maven.project.make_dirs") as mock_make_dirs:
        with patch("vang.maven.project.get_pom", return_value="pom") as mock_get_pom:
            with patch("vang.maven.project.open") as mock_open:
                make_project(
                    "output_dir",
                    "1.8",
                    "group_id",
                    "artifact_id",
                    "version",
                    "packaging",
                )
                assert mock_make_dirs.mock_calls == [
                    call(
                        "output_dir",
                        "group_id",
                        "artifact_id",
                        "packaging",
                    )
                ]
                assert mock_get_pom.mock_calls == [
                    call(
                        "1.8",
                        "group_id",
                        "artifact_id",
                        "version",
                        "packaging",
                    )
                ]
                assert mock_open.mock_calls == [
                    call("output_dir/pom.xml", "wt", encoding="utf-8"),
                    call().__enter__(),
                    call().__enter__().write("pom"),
                    call().__exit__(None, None, None),
                ]


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", [call("slask", "11", "mygroup", "slask", "1.0.0-SNAPSHOT", "jar")]),
        ("input", [call("input", "input", "input", "input", "input", "input")]),
    ],
)
def test_project(input, expected):
    with patch("vang.maven.project.input", return_value=input) as mock_make_project:
        with patch("vang.maven.project.make_project") as mock_make_project:
            project()
            assert mock_make_project.mock_calls == expected
