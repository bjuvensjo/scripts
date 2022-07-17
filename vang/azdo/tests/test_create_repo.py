from json import dumps
from unittest.mock import Mock, call, patch

import pytest
from requests import Response
from vang.azdo.create_repo import create_repo, parse_args


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            "r1",
            [
                call(200),
                call(
                    "If you already have code ready to be pushed to this repository then run this in your terminal."
                ),
                call(
                    "    git remote add origin https://myorg@myazure/myorg/myproject/_git/r1\n"
                    "    git push -u origin --all"
                ),
                call("(The commands are copied to the clipboard)"),
            ],
        )
    ],
)
@patch("vang.azdo.create_repo.print")
@patch("vang.azdo.create_repo.post")
def test_create_repo(mock_post, mock_print, args, expected):
    mock_post.return_value = Mock(
        Response,
        status_code=200,
        text=dumps(
            # Only used parts of response
            {"remoteUrl": "https://myorg@myazure/myorg/myproject/_git/r1"}
        ),
    )
    argv = f"dummy -t mytoken -o myorg -p myproject -au https://myazure --no-verify_certificate {args}".strip().split(
        " "
    )
    create_repo(**parse_args(argv[1:]).__dict__)
    assert mock_post.mock_calls == [
        call(
            json={"name": "r1"},
            url="https://myazure/myorg/myproject/_apis/git/repositories?api-version=6.1-preview.1",
            auth=("", "mytoken"),
            verify=False,
        ),
        call().raise_for_status(),
    ]
    assert mock_print.mock_calls == expected
