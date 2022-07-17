from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.create_build_definition import create_build_definition, parse_args


@pytest.mark.parametrize(
    "args, expected",
    [("r1", [call(200)])],
)
@patch("vang.azdo.create_build_definition.print")
@patch("vang.azdo.create_build_definition.post")
def test_create_build_definition(mock_post, mock_print, args, expected):
    mock_post.return_value = Mock(
        Response,
        status_code=200,
        text="{}",  # Only used parts of response
    )
    argv = f"dummy -t mytoken -o myorg -p myproject -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    create_build_definition(**parse_args(argv[1:]).__dict__)
    assert mock_post.mock_calls == [
        call(
            json={
                "triggers": [
                    {
                        "branchFilters": [],
                        "pathFilters": [],
                        "settingsSourceType": 2,
                        "batchChanges": False,
                        "maxConcurrentBuildsPerBranch": 1,
                        "triggerType": "continuousIntegration",
                    }
                ],
                "process": {"yamlFilename": "azure-pipelines.yml", "type": 2},
                "repository": {"name": "r1", "type": "TfsGit"},
                "queue": {"id": 8},
                "name": "r1",
            },
            url="https://myazure/myorg/myproject/_apis/build/definitions?api-version=6.1-preview.7",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
