#!/usr/bin/env python3
from unittest.mock import call, patch

from vang.bitbucket.api import call as bitbucket_call


@patch('vang.bitbucket.api.post', autospec=True)
@patch('vang.bitbucket.api.get', autospec=True)
def test_call(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'key': 'value'}
    assert 200 == bitbucket_call(
        '/uri',
        only_response_code=True,
        rest_url='http://rest_url',
        username='username',
        password='password',
        verify_certificate=True)
    assert [
               call(auth=('username', 'password'), url='http://rest_url/uri', verify=True),
           ] == mock_get.mock_calls

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'key': 'value'}
    assert {
               'key': 'value'
           } == bitbucket_call(
        '/uri',
        request_data={'request_key': 'request_value'},
        method='POST',
        rest_url='http://rest_url',
        username='username',
        password='password',
        verify_certificate=False
    )
    assert [
               call(
                   auth=('username', 'password'),
                   json={'request_key': 'request_value'},
                   url='http://rest_url/uri',
                   verify=False,
               ),
               call().text.__bool__(),
               call().json()
           ] == mock_post.mock_calls
