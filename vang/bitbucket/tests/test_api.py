from unittest.mock import call, patch

from vang.bitbucket.api import call as bitbucket_call


@patch("vang.bitbucket.api.post", autospec=True)
@patch("vang.bitbucket.api.get", autospec=True)
def test_call(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}
    assert (
        bitbucket_call(
            "/uri",
            only_response_code=True,
            rest_url="http://rest_url",
            username="username",
            password="password",
            verify_certificate=True,
        )
        == 200
    )
    assert mock_get.mock_calls == [
        call(auth=("username", "password"), url="http://rest_url/uri", verify=True),
    ]

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"key": "value"}
    assert bitbucket_call(
        "/uri",
        request_data={"request_key": "request_value"},
        method="POST",
        rest_url="http://rest_url",
        username="username",
        password="password",
        verify_certificate=False,
    ) == {"key": "value"}
    assert mock_post.mock_calls == [
        call(
            auth=("username", "password"),
            json={"request_key": "request_value"},
            url="http://rest_url/uri",
            verify=False,
        ),
        call().text.__bool__(),
        call().json(),
    ]
