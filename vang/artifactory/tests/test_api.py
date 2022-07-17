from unittest.mock import call, patch

from vang.artifactory.api import call as artifactory_call, create_request

import pytest


@pytest.mark.parametrize(
    "return_code, output",
    [
        (200, ""),
        (200, "output"),
    ],
)
@patch("vang.artifactory.api.urlopen", autospec=True)
@patch("vang.artifactory.api.create_request", autospec=True)
def test_call(mock_create_request, mock_urlopen, return_code, output):
    mock_create_request.return_value = "request"
    mock_urlopen.return_value.getcode.return_value = return_code
    mock_urlopen.return_value.read.return_value = (
        str.encode(f'"{output}"') if output else ""
    )
    expected = output or return_code

    assert artifactory_call(
        "/uri",
        {"extra_header": "extra-header-value"},
        b"request_data",
        "POST",
        "rest_url",
        "username",
        "password",
    ) == expected

    assert [
        call(
            {
                "Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
                "Content-Type": "application/json",
                "extra_header": "extra-header-value",
            },
            "POST",
            b"request_data",
            "rest_url/uri",
        )
    ] == mock_create_request.mock_calls

    expected = (
        [call("request"), call().read()]
        if output
        else [call("request"), call().read(), call().getcode()]
    )
    assert mock_urlopen.mock_calls == expected


def test_create_request():
    assert create_request(
        {"Authorization": "basic_auth_header", "Content-Type": "application/json"},
        "POST",
        '"request_data"',
        "http://rest_url/uri",
    )
