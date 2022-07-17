from pytest import raises

from unittest.mock import call, patch, mock_open

from vang.artifactory.publish import get_checksum_headers
from vang.artifactory.publish import get_checksums
from vang.artifactory.publish import get_pom_publish_name
from vang.artifactory.publish import get_publish_data
from vang.artifactory.publish import publish
from vang.artifactory.publish import parse_args
from vang.artifactory.publish import publish_maven_artifact
from vang.artifactory.publish import read_file

import pytest


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=b"Nobody inspects the spammish repetition",
)
def test_read_file(mock_file):
    assert read_file("file_path") == b"Nobody inspects the spammish repetition"
    mock_file.assert_called_with("file_path", "rb")


def test_get_checksums():
    md5, sha1, sha256 = get_checksums(b"Nobody inspects the spammish repetition")
    assert md5 == "bb649c83dd1ea5c9d9dec9a18df0ffe9"
    assert sha1 == "531b07a0f5b66477a21742d2827176264f4bbfe2"
    assert sha256 == "031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406"


def test_get_checksum_headers():
    assert get_checksum_headers(5, 1, 256) == {
        "X-Checksum-Md5": 5,
        "X-Checksum-Sha1": 1,
        "X-Checksum-Sha256": 256,
    }


@pytest.mark.parametrize(
    "params, expected",
    [
        (
            (
                "/foo/bar/business.baz-1.0.0-SNAPSHOT.pom",
                "business.baz",
                "1.0.0-SNAPSHOT",
            ),
            "business.baz-1.0.0-SNAPSHOT.pom",
        ),
        (
            (
                "/foo/bar/pom.xml",
                "business.baz",
                "1.0.0-SNAPSHOT",
            ),
            "business.baz-1.0.0-SNAPSHOT.pom",
        ),
    ],
)
def test_get_pom_publish_name(params, expected):
    assert get_pom_publish_name(*params) == expected


@patch("vang.artifactory.publish.get_checksum_headers")
@patch("vang.artifactory.publish.get_checksums")
@patch("vang.artifactory.publish.read_file")
def test_get_publish_data(
    mock_read_file,
    mock_get_checksums,
    mock_get_checksum_headers,
):
    mock_read_file.return_value = b"Hello World!"
    mock_get_checksums.return_value = [5, 1, 256]
    mock_get_checksum_headers.return_value = {
        "X-Checksum-Md5": 5,
        "X-Checksum-Sha1": 1,
        "X-Checksum-Sha256": 256,
    }
    assert get_publish_data(
        "/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT",
        "/foo/bar/foo.pom",
        "business.baz-1.0.0-SNAPSHOT.pom",
    ) == {
        "checksum_headers": {
            "X-Checksum-Md5": 5,
            "X-Checksum-Sha1": 1,
            "X-Checksum-Sha256": 256,
        },
        "content": b"Hello World!",
        "uri": "/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT/business.baz-1.0.0-SNAPSHOT.pom",
    }


@patch("vang.artifactory.publish.api.call")
@patch("vang.artifactory.publish.glob")
@patch("vang.artifactory.publish.get_pom_publish_name")
@patch("vang.artifactory.publish.get_publish_data")
@patch("vang.artifactory.publish.get_artifact_base_uri")
@patch("vang.artifactory.publish.get_pom_info")
@patch("vang.artifactory.publish.get_pom_path")
def test_publish_maven_artifact(
    mock_get_pom_path,
    mock_get_pom_info,
    mock_get_artifact_base_uri,
    mock_get_publish_data,
    mock_get_pom_publish_name,
    mock_glob,
    mock_call,
):
    mock_get_pom_path.return_value = "pom_path"
    mock_get_pom_info.return_value = {
        "pom_path": "pom_path",
        "artifact_id": "artifact_id",
        "group_id": "parent_group_id",
        "version": "parent_version",
        "packaging": "packaging",
    }
    mock_get_artifact_base_uri.return_value = "base_uri"
    mock_get_publish_data.return_value = {
        "checksum_headers": {
            "X-Checksum-Md5": 5,
            "X-Checksum-Sha1": 1,
            "X-Checksum-Sha256": 256,
        },
        "content": b"content",
        "uri": "uri",
    }
    mock_get_pom_publish_name.return_value = "pom_publish_name"
    mock_glob.side_effect = [["foo.jar"], ["bar.war"]] * 2
    mock_call.return_value = '"response"'

    assert list(publish_maven_artifact("repository", ["d1", "d2"])) == [
        ['"response"', '"response"', '"response"'],
        ['"response"', '"response"', '"response"'],
    ]


@patch("vang.artifactory.publish.print")
@patch("vang.artifactory.publish.publish_maven_artifact")
def test_main(mock_publish_maven_artifact, mock_print):
    mock_publish_maven_artifact.return_value = ["'response'"]
    publish("repository", ["d1", "d2"])
    assert mock_publish_maven_artifact.mock_calls == [call("repository", ["d1", "d2"])]
    assert mock_print.mock_calls == [call('"response"')]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "1 2",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "repository",
            {
                "repository": "repository",
                "dirs": ["."],
            },
        ],
        [
            "repository -d d1 d2",
            {
                "repository": "repository",
                "dirs": ["d1", "d2"],
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
