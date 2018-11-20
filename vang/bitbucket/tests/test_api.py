#!/usr/bin/env python3
from unittest.mock import call, patch

from vang.bitbucket.api import call as bitbucket_call, create_request

import pytest


@pytest.mark.parametrize("return_code, output", [
    (200, ''),
    (200, 'output'),
])
def test_call(return_code, output):
    with patch(
            'vang.bitbucket.api.create_request',
            autospec=True,
            return_value='request') as mock_create_request:
        with patch('vang.bitbucket.api.urlopen', autospec=True) as mock_urlopen:
            mock_urlopen.return_value.getcode.return_value = return_code
            mock_urlopen.return_value.read.return_value = str.encode(
                f'"{output}"') if output else ''
            expected = output or return_code
            assert expected == bitbucket_call(
                '/uri',
                'request_data',
                'POST',
                'rest_url',
                'username',
                'password',
            )
            assert [
                call(
                    'Basic dXNlcm5hbWU6cGFzc3dvcmQ=',
                    'POST',
                    'request_data',
                    'rest_url/uri',
                )
            ] == mock_create_request.mock_calls

            expected = [call('request'), call().read()] if output else [
                call('request'),
                call().read(), call().getcode()
            ]
            assert expected == mock_urlopen.mock_calls


def test_create_request():
    assert create_request('basic_auth_header', 'POST', '"request_data"',
                          'http://rest_url/uri')
