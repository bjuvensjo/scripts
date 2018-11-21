#!/usr/bin/env python3
from unittest.mock import call, patch

from pytest import raises

from vang.bitbucket.has_tag import has_tag
from vang.bitbucket.has_tag import main
from vang.bitbucket.has_tag import parse_args

import pytest


@pytest.fixture
def tags_fixture():
    return [
        (('project_key', 'repo_slug1'), {
            'id': 'refs/tags/t1',
            'displayId': 't1',
            'type': 'TAG',
            'latestCommit': 'f89ed5',
            'latestChangeset': 'f89ed5',
            'hash': '430f79'
        }),
        (('project_key', 'repo_slug2'), {
            'id': 'refs/tags/t1',
            'displayId': 't1',
            'type': 'TAG',
            'latestCommit': 'f89ed5',
            'latestChangeset': 'f89ed5',
            'hash': '430f79'
        }),
    ]


@pytest.mark.parametrize("tag, expected", [('t1', True), ('t2', False)])
@patch('vang.bitbucket.has_tag.get_tags', autospec=True)
def test_has_tag(mock_get_tags, tag, expected, tags_fixture):
    mock_get_tags.return_value = tags_fixture
    assert [
        (['project_key', 'repo_slug1'], expected),
        (['project_key', 'repo_slug2'], expected),
    ] == list(
        has_tag(
            [
                ['project_key', 'repo_slug1'],
                ['project_key', 'repo_slug2'],
            ],
            tag,
        ))


@patch('vang.bitbucket.has_tag.print')
@patch('vang.bitbucket.has_tag.get_repo_specs', autospec=True)
@patch('vang.bitbucket.has_tag.get_tags', autospec=True)
def test_main(mock_get_tags, mock_get_repo_specs, mock_print, tags_fixture):
    mock_get_tags.return_value = tags_fixture
    mock_get_repo_specs.return_value = [
        ['project_key', 'repo_slug1'],
        ['project_key', 'repo_slug2'],
    ]
    main('t1', repos=['project_key/repo_slug1', 'project_key/repo_slug2'])
    assert [
        call(None, [
            'project_key/repo_slug1',
            'project_key/repo_slug2',
        ], None)
    ] == mock_get_repo_specs.mock_calls
    assert [
        call('project_key/repo_slug1, t1: True'),
        call('project_key/repo_slug2, t1: True')
    ] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '-d d -r r',
    '-d d -p p',
    '-r r -p p',
    '1 2',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['t', {
        'tag': 't',
        'dirs': ['.'],
        'projects': None,
        'repos': None,
    }],
    [
        't -d d1 d2',
        {
            'tag': 't',
            'dirs': ['d1', 'd2'],
            'projects': None,
            'repos': None
        }
    ],
    [
        't -r p/r1 p/r2',
        {
            'tag': 't',
            'dirs': ['.'],
            'projects': None,
            'repos': ['p/r1', 'p/r2']
        }
    ],
    [
        't -p p1 p2',
        {
            'tag': 't',
            'dirs': ['.'],
            'projects': ['p1', 'p2'],
            'repos': None
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
