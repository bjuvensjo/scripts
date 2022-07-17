from unittest.mock import call, patch

from vang.maven.pom import get_pom_paths
from vang.maven.pom import get_pom_info
from xml.etree.ElementTree import fromstring

import pytest


@patch("vang.maven.pom.glob", autospec=True, return_value=["p1", "p2"])
def test_get_pom_paths(mock_glob):
    assert len(get_pom_paths("root")) == 2
    assert mock_glob.mock_calls == [call("root/**/pom.xml", recursive=True)]


@pytest.mark.parametrize(
    "pom, expected",
    [
        (
            """<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
        http://maven.apache.org/xsd/maven-4.0.0.xsd">
   <groupId>group_id</groupId>
   <artifactId>artifact_id</artifactId>
   <version>version</version>
   <packaging>packaging</packaging>
</project>
""",
            {
                "pom_path": "pom_path",
                "artifact_id": "artifact_id",
                "group_id": "group_id",
                "version": "version",
                "packaging": "packaging",
            },
        ),
        (
            """<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
        http://maven.apache.org/xsd/maven-4.0.0.xsd">
   <artifactId>artifact_id</artifactId>
   <packaging>packaging</packaging>
    <parent>
      <groupId>parent_group_id</groupId>
      <version>parent_version</version>
    </parent>
</project>
""",
            {
                "pom_path": "pom_path",
                "artifact_id": "artifact_id",
                "group_id": "parent_group_id",
                "version": "parent_version",
                "packaging": "packaging",
            },
        ),
    ],
)
def test_get_pom_info_no_parent(pom, expected):
    with patch("vang.maven.pom.parse", autospec=True, return_value=fromstring(pom)):
        assert get_pom_info("pom_path") == expected
