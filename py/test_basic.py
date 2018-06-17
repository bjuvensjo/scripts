from argparse import Namespace
from unittest.mock import patch, call
from pytest import raises
from basic import get_basic_auth
from basic import get_basic_auth_header
from basic import main
from basic import parse_args


def test_get_basic_auth():
    assert 'Basic dXNlcm5hbWU6cGFzc3dvcmQ=' == \
        get_basic_auth('username', 'password')


def test_get_basic_auth_header():
    assert 'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=' == \
        get_basic_auth_header('username', 'password')


def test_parse_args():
    assert Namespace(
        password='password',
        username='username') == parse_args(['-u', 'username', '-p', 'password'])
    assert Namespace(
        password='password', username='username') == parse_args(
            ['--username', 'username', '--password', 'password'])
    with patch('basic.environ', {'U': 'username', 'P': 'password'}):
        assert Namespace(
            password='password', username='username') == parse_args([])
    with raises(SystemExit) as se:
        parse_args(['x'])
    assert 2 == se.value.code


def test_main():
    with patch('basic.name',
               'posix'), patch('basic.system') as mock_system, patch(
                   'builtins.print') as mock_print:
        main('username', 'password')
        assert [
            call(
                "echo 'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=\\c' | pbcopy"
            )
        ] == mock_system.mock_calls
        assert [
            call(
                "'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=' copied to clipboard"
            )
        ] == mock_print.mock_calls
    with patch('basic.name',
               'not-posix'), patch('builtins.print') as mock_print:
        main('username', 'password')
        assert [call('Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=')
                ] == mock_print.mock_calls
