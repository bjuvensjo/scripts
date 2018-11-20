#!/usr/bin/env python3
from unittest.mock import call, patch

from vang.jenkins.api import call as jenkins_call, create_request


@patch('vang.jenkins.api.create_request', autospec=True, return_value='request')
@patch('vang.jenkins.api.urlopen', autospec=True)
def test_call(mock_urlopen, mock_create_request):
    mock_urlopen.return_value.getcode.return_value = 200
    mock_urlopen.return_value.read.return_value = b'"response_data"'
    assert 200 == jenkins_call('/uri', only_response_code=True)

    assert [call('request'), call().getcode()] == mock_urlopen.mock_calls

    mock_urlopen.reset_mock()
    mock_create_request.reset_mock()
    assert 'response_data' == jenkins_call(
        '/uri',
        request_data='"request_data"',
        method='POST',
        rest_url='http://rest_url',
        username='username',
        password='password')

    assert [call('request'), call().getcode(),
            call().read()] == mock_urlopen.mock_calls

    assert [
        call('Basic dXNlcm5hbWU6cGFzc3dvcmQ=', 'POST', '"request_data"',
             'http://rest_url/uri')
    ] == mock_create_request.mock_calls


def test_create_request():
    assert create_request(
        'basic_auth_header',
        'POST',
        '"request_data"',
        'http://rest_url/uri',
    )
