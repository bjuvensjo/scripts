#!/usr/bin/env python3
from unittest.mock import call, patch

from vang.jenkins.api import call as jenkins_call


@patch('vang.jenkins.api.post', autospec=True)
@patch('vang.jenkins.api.get', autospec=True)
def test_call(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'key': 'value'}
    assert 200 == jenkins_call(
        '/uri',
        only_response_code=True,
        rest_url='http://rest_url',
        username='username',
        password='password',
        verify_certificate=False)
    assert [
               call(auth=('username', 'password'), url='http://rest_url/uri', verify=False),
           ] == mock_get.mock_calls

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'key': 'value'}
    assert {
               'key': 'value'
           } == jenkins_call(
        '/uri',
        request_data={'request_key': 'request_value'},
        method='POST',
        rest_url='http://rest_url',
        username='username',
        password='password',
        verify_certificate=True)
    assert [
               call(
                   auth=('username', 'password'),
                   json={'request_key': 'request_value'},
                   url='http://rest_url/uri',
                   verify=True
               ),
               call().text.__bool__(),
               call().json()
           ] == mock_post.mock_calls
