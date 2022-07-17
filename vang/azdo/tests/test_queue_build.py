from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.queue_build import parse_args, queue_build


@pytest.mark.parametrize(
    "args, expected",
    [
        ("b1 release/1.0.x", [call(200)]),
    ],
)
@patch("vang.azdo.queue_build.print")
@patch("vang.azdo.queue_build.post")
@patch("vang.azdo.queue_build.get")
def test_queue_build(mock_get, mock_post, mock_print, args, expected):
    mock_get.return_value = Mock(
        Response,
        status_code=200,
        text=dumps(
            {
                "value": [
                    {
                        "id": 4,
                    }
                ],
            }
        ),  # Only used parts of response
    )
    mock_post.return_value = Mock(
        Response, status_code=200, text=dumps({})
    )  # Only used parts of response
    argv = f"dummy -t mytoken -o myorg -p myproject -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    queue_build(**parse_args(argv[1:]).__dict__)
    assert mock_post.mock_calls == [
        call(
            json={"definition": {"id": 4}, "sourceBranch": "refs/heads/release/1.0.x"},
            url="https://myazure/myorg/myproject/_apis/build/builds?api-version=6.1-preview.6",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
