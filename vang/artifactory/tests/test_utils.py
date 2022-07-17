from unittest.mock import patch
from pytest import raises

from vang.artifactory.utils import get_artifact_base_uri
from vang.artifactory.utils import get_pom_path


@patch("vang.artifactory.utils.glob")
@patch("vang.artifactory.utils.exists")
def test_get_pom_path(mock_exists, mock_glob):
    mock_exists.return_value = True
    assert get_pom_path("/foo/bar") == "/foo/bar/pom.xml"
    mock_exists.assert_called_with("/foo/bar/pom.xml")

    mock_exists.return_value = False
    mock_glob.return_value = ["/foo/bar/foo.pom"]
    assert get_pom_path("/foo/bar") == "/foo/bar/foo.pom"

    mock_glob.return_value = [
        "/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-20150610.210152-141.pom",
        "/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom",
    ]
    assert (
        get_pom_path("/signing.updatesigning/1.0.0-SNAPSHOT")
        == "/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom"
    )

    mock_glob.return_value = []
    with raises(ValueError):
        get_pom_path("/foo/bar")


def test_get_artifact_base_uri():
    assert (
        get_artifact_base_uri(
            "repo",
            "com.foo.bar",
            "business.baz",
            "1.0.0-SNAPSHOT",
        )
        == "/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT"
    )
