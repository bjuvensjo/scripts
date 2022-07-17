from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.get_project import get_project, parse_args


@pytest.mark.parametrize(
    "args, expected",
    [
        ("-p p1", [call({"id": "1"})]),
        ("-p p1 -i", [call("1")]),
    ],
)
@patch("vang.azdo.get_project.print")
@patch("vang.azdo.get_project.get")
@patch("vang.azdo.get_project.do_list_projects")
def test_get_project(mock_do_list_projects, mock_get, mock_print, args, expected):
    mock_do_list_projects.return_value = {
        "value": [{"name": "p1", "id": "1"}]
    }  # Only used parts of response
    mock_get.return_value = Mock(
        Response,
        status_code=200,
        text=dumps(
            {
                "id": "1",
            }
        ),  # Only used parts of response
    )
    argv = f"dummy -t mytoken -o myorg -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    get_project(**parse_args(argv[1:]).__dict__)
    assert mock_get.mock_calls == [
        call(
            url="https://myazure/myorg/_apis/projects/1?api-version=6.1-preview.4",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
