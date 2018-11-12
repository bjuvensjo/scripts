from unittest.mock import call, patch

from pytest import raises

from vang.misc.basic import get_basic_auth
from vang.misc.basic import get_basic_auth_header
from vang.misc.basic import main
from vang.misc.basic import parse_args


def test_get_basic_auth():
    assert 'Basic dXNlcm5hbWU6cGFzc3dvcmQ=' == \
           get_basic_auth('username', 'password')


def test_get_basic_auth_header():
    assert 'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=' == \
           get_basic_auth_header('username', 'password')


def test_parse_args():
    for args in ['foo']:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    with patch('vang.misc.basic.environ', {'U': 'username', 'P': 'password'}):
        for args, pargs in [
            ['', {
                'password': 'password',
                'username': 'username'
            }],
            ['-u u -p p', {
                'password': 'p',
                'username': 'u'
            }],
            ['-u u', {
                'password': 'password',
                'username': 'u'
            }],
            ['-p p', {
                'password': 'p',
                'username': 'username'
            }],
        ]:
            assert pargs == parse_args(args.split(' ') if args else []).__dict__


def test_main():
    with patch('vang.misc.basic.name',
               'posix'), patch('vang.misc.basic.system') as mock_system, patch(
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
    with patch('vang.misc.basic.name',
               'not-posix'), patch('builtins.print') as mock_print:
        main('username', 'password')
        assert [call('Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=')
                ] == mock_print.mock_calls
