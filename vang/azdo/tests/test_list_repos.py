from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.list_repos import list_repos, parse_args

# Only used parts of response
response = {
    "value": [
        {
            "name": "r1",
            "remoteUrl": "https://myorg@myazure/myorg/myproject/_git/r1",
        },
        {
            "name": "r2",
            "remoteUrl": "https://myorg@myazure/myorg/myproject/_git/r2",
        },
    ]
}


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            "",
            [call(response)],
        ),
        (
            "-n",
            [call("r1"), call("r2")],
        ),
        (
            "-r",
            [call("myorg/myproject/r1"), call("myorg/myproject/r2")],
        ),
        (
            "-u",
            [
                call("https://myorg@myazure/myorg/myproject/_git/r1"),
                call("https://myorg@myazure/myorg/myproject/_git/r2"),
            ],
        ),
    ],
)
@patch("vang.azdo.list_repos.print")
@patch("vang.azdo.list_repos.get")
def test_list_repos(mock_get, mock_print, args, expected):
    mock_get.return_value = Mock(Response, status_code=200, text=dumps(response))
    argv = f"dummy -t mytoken -o myorg -p myproject -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    list_repos(**parse_args(argv[1:]).__dict__)
    assert mock_get.mock_calls == [
        call(
            url="https://myazure/myorg/myproject/_apis/git/repositories?includeLinks=False&includeAllUrls=False&includeHidden=False&api-version=6.1-preview.1",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
