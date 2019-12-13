#!/usr/bin/env python3
from unittest.mock import patch, call

from vang.tfs.api import call as tfs_call


@patch('vang.tfs.api.post', autospec=True)
@patch('vang.tfs.api.get', autospec=True)
def test_call(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'key': 'value'}
    assert 200 == tfs_call(
        '/uri',
        only_response_code=True,
        rest_url='http://rest_url',
        token='token')
    assert [
               call(auth=('', 'token'), url='http://rest_url/uri', verify=False),
           ] == mock_get.mock_calls

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'key': 'value'}
    assert {
               'key': 'value'
           } == tfs_call(
        '/uri',
        request_data={'request_key': 'request_value'},
        method='POST',
        rest_url='http://rest_url',
        token='token')
    assert [
               call(
                   auth=('', 'token'),
                   json={'request_key': 'request_value'},
                   url='http://rest_url/uri',
                   verify=False,
               ),
               call().text.__bool__(),
               call().json()
           ] == mock_post.mock_calls
