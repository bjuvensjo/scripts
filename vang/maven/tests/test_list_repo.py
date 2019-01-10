#!/usr/bin/env python3
from unittest.mock import call, patch
from pytest import raises

from vang.maven.list_repo import get_artifacts
from vang.maven.list_repo import has_ending
from vang.maven.list_repo import is_included
from vang.maven.list_repo import main
from vang.maven.list_repo import parse_args

import pytest


@pytest.mark.parametrize("endings, file_names, expected", [
    (['pom', 'jar'], [], False),
    (['pom', 'jar'], ['foo'], False),
    (['pom', 'jar'], ['foo.baz', 'foo.bar'], False),
    (['pom', 'jar'], ['foo.pom', 'foo.bar'], True),
    (['pom', 'jar'], ['foo.jar', 'foo.bar'], True),
])
def test_has_ending(endings, file_names, expected):
    assert expected == has_ending(endings, file_names)


@pytest.mark.parametrize("snapshots, dir_path, expected", [
    (False, 'path-snapshot', False),
    (True, 'path-snapshot', True),
    (False, 'path', True),
    (True, 'path', True),
])
def test_is_included(snapshots, dir_path, expected):
    assert expected == is_included(snapshots, dir_path)


@pytest.mark.parametrize("snapshots, expected", [
    (False, ['dir_path']),
    (True, ['dir_path', 'dir_path-SNAPSHOT']),
])
def test_get_artifacts(snapshots, expected):
    with patch(
            'vang.maven.list_repo.walk',
            return_value=[
                [
                    'repo_dir/dir_path',
                    ['dir_names'],
                    ['file_names.pom'],
                ],
                [
                    'repo_dir/dir_path-SNAPSHOT',
                    ['dir_names'],
                    ['file_names.pom'],
                ],
            ]):
        assert expected == get_artifacts('repo_dir', snapshots=snapshots)


@pytest.mark.parametrize("args", [
    '',
    '1 2',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['repository', {
        'repo_dir': 'repository',
    }],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ')).__dict__


@patch('vang.maven.list_repo.print')
@patch('vang.maven.list_repo.get_artifacts')
def test_main(mock_get_artifacts, mock_print):
    mock_get_artifacts.return_value = [
        'ch/qos/logback/logback-core/1.1.11',
        'ch/qos/logback/logback-core/1.2.3',
    ]
    main('repo_dir')
    assert [
        call('<dependency>\n'
             '    <groupId>ch.qos.logback</groupId>\n'
             '    <artifactId>logback-core</artifactId>\n'
             '    <version>1.1.11</version>\n'
             '</dependency>'),
        call('<dependency>\n'
             '    <groupId>ch.qos.logback</groupId>\n'
             '    <artifactId>logback-core</artifactId>\n'
             '    <version>1.2.3</version>\n'
             '</dependency>')
    ] == mock_print.mock_calls
