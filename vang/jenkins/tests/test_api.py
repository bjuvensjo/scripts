from unittest.mock import call, patch

from vang.jenkins.api import call as jenkins_call


@patch("vang.jenkins.api.post", autospec=True)
@patch("vang.jenkins.api.get", autospec=True)
def test_call(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}
    assert (
        jenkins_call(
            "/uri",
            only_response_code=True,
            rest_url="http://rest_url",
            username="username",
            password="password",
            verify_certificate=False,
        )
        == 200
    )
    assert mock_get.mock_calls == [
        call(auth=("username", "password"), url="http://rest_url/uri", verify=False),
    ]

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"key": "value"}
    assert jenkins_call(
        "/uri",
        request_data={"request_key": "request_value"},
        method="POST",
        rest_url="http://rest_url",
        username="username",
        password="password",
        verify_certificate=True,
    ) == {"key": "value"}
    assert mock_post.mock_calls == [
        call(
            auth=("username", "password"),
            json={"request_key": "request_value"},
            url="http://rest_url/uri",
            verify=True,
        ),
        call().text.__bool__(),
        call().json(),
    ]
