from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.list_builds import list_builds, parse_args

# Only used parts of response
response = {
    "value": [{}],
}


@pytest.mark.parametrize(
    "args, expected",
    [
        ("", [call(response)]),
    ],
)
@patch("vang.azdo.list_builds.print")
@patch("vang.azdo.list_builds.get")
def test_list_builds(mock_get, mock_print, args, expected):
    mock_get.return_value = Mock(Response, status_code=200, text=dumps(response))
    argv = f"dummy -t mytoken -o myorg -p myproject -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    list_builds(**parse_args(argv[1:]).__dict__)
    assert mock_get.mock_calls == [
        call(
            url="https://myazure/myorg/myproject/_apis/build/builds?api-version=6.1-preview.6",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
