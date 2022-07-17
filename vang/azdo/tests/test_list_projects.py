from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.list_projects import list_projects, parse_args

# Only used parts of response
response = {
    "value": [
        {
            "name": "p1",
        },
        {
            "name": "p2",
        },
    ],
}


@pytest.mark.parametrize(
    "args, expected",
    [
        ("", [call(response)]),
        ("-n", [call("p1"), call("p2")]),
        ("-r", [call("myorg/p1"), call("myorg/p2")]),
    ],
)
@patch("vang.azdo.list_projects.print")
@patch("vang.azdo.list_projects.get")
def test_list_projects(mock_get, mock_print, args, expected):
    mock_get.return_value = Mock(Response, status_code=200, text=dumps(response))
    argv = f"dummy -t mytoken -o myorg -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    list_projects(**parse_args(argv[1:]).__dict__)
    assert mock_get.mock_calls == [
        call(
            url="https://myazure/myorg/_apis/projects?api-version=6.1-preview.4",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
