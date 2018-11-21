#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.pio.zip_read import is_included
from vang.pio.zip_read import main
from vang.pio.zip_read import parse_args

import pytest


@pytest.mark.parametrize("patterns, name, expected", [
    (['.*'], 'foo.py', True),
    (['foo.+'], 'foo.py', True),
    (['.+o.+'], 'foo.py', True),
    (['.+\.py'], 'foo.py', True),
    (['.+\.py', 'bar'], 'foo.py', True),
    (['.+\.p'], 'foo.py', False),
    (['foo'], 'foo.py', False),
])
def test_is_included(patterns, name, expected):
    assert expected == is_included(patterns, name)


@pytest.mark.parametrize("only_content, encoding, expected", [
    (False, 'utf-8', [
        call('########################################'
             '########################################'),
        call('#####', 'f', '#####'),
        call('1'),
        call('#########################################'
             '#######################################'),
        call('#####', 'c', '#####'),
        call('1')
    ]),
])
@patch('vang.pio.zip_read.print')
@patch('vang.pio.zip_read.zip_read', autospec=True)
def test_main(mock_zip_read, mock_print, only_content, encoding, expected):
    mock_zip_read.side_effect = [('f1', 'c1'), ('f2', 'c2')]

    main('zip_file', ['p1', 'p2'], only_content, encoding)

    assert [call('zip_file', ['p1', 'p2'], 'utf-8')] == mock_zip_read.mock_calls
    assert expected == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '1 2',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    [
        'zip_file',
        {
            'zip_file': 'zip_file',
            'patterns': ['.*'],
            'only_content': False,
            'encoding': 'utf-8'
        }
    ],
    [
        'zip_file -p p1 p2 -o -e e',
        {
            'zip_file': 'zip_file',
            'patterns': ['p1', 'p2'],
            'only_content': True,
            'encoding': 'e'
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__
