from os import environ
from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.nexus3.publish import get_pom_publish_name
from vang.nexus3.publish import get_publish_data
from vang.nexus3.publish import main
from vang.nexus3.publish import parse_args
from vang.nexus3.publish import publish_maven_artifact


@pytest.mark.parametrize("params, expected",
                         [(
                                 (
                                         '/foo/bar/business.baz-1.0.0-SNAPSHOT.pom',
                                         'business.baz',
                                         '1.0.0-SNAPSHOT',
                                 ),
                                 'business.baz-1.0.0-SNAPSHOT.pom',
                         ),
                             (
                                     (
                                             '/foo/bar/pom.xml',
                                             'business.baz',
                                             '1.0.0-SNAPSHOT',
                                     ),
                                     'business.baz-1.0.0-SNAPSHOT.pom',
                             )])
def test_get_pom_publish_name(params, expected):
    assert expected == get_pom_publish_name(*params)


def test_get_publish_data():
    assert {
               'file_path': '/foo/bar/foo.pom',
               'repository_path': '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT/business.baz-1.0.0-SNAPSHOT.pom',
           } == get_publish_data(
        '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT',
        '/foo/bar/foo.pom',
        'business.baz-1.0.0-SNAPSHOT.pom',
    )


@patch('vang.nexus3.publish.upload')
@patch('vang.nexus3.publish.glob')
@patch('vang.nexus3.publish.get_pom_publish_name')
@patch('vang.nexus3.publish.get_publish_data')
@patch('vang.nexus3.publish.get_artifact_base_uri')
@patch('vang.nexus3.publish.get_pom_info')
@patch('vang.nexus3.publish.get_pom_path')
def test_publish_maven_artifact(
        mock_get_pom_path,
        mock_get_pom_info,
        mock_get_artifact_base_uri,
        mock_get_publish_data,
        mock_get_pom_publish_name,
        mock_glob,
        mock_upload,
):
    mock_get_pom_path.return_value = 'pom_path'
    mock_get_pom_info.return_value = {
        'pom_path': 'pom_path',
        'artifact_id': 'artifact_id',
        'group_id': 'parent_group_id',
        'version': 'parent_version',
        'packaging': 'packaging',
    }
    mock_get_artifact_base_uri.return_value = 'base_uri'
    mock_get_publish_data.return_value = {
        'file_path': 'file_path',
        'repository_path': 'repository_path'
    }
    mock_get_pom_publish_name.return_value = 'pom_publish_name'
    mock_glob.side_effect = [['foo.jar'], ['bar.war']] * 2
    mock_upload.return_value = 201

    assert [[201, 201, 201],
            [201, 201, 201]] == list(publish_maven_artifact('repository', ['d1', 'd2'], 'url', 'username', 'password'))


@patch('vang.nexus3.publish.print')
@patch('vang.nexus3.publish.publish_maven_artifact')
def test_main(mock_publish_maven_artifact, mock_print):
    mock_publish_maven_artifact.return_value = [201]
    main('repository', ['d1', 'd2'], 'url', 'username', 'password')
    assert [call('repository', ['d1', 'd2'], 'url', 'username', 'password')] == mock_publish_maven_artifact.mock_calls
    assert [call(201)] == mock_print.mock_calls


@pytest.mark.parametrize("args", [
    '',
    '1 2',
])
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(' ') if args else args)


@pytest.mark.parametrize("args, expected", [
    ['repository', {
        'repository': 'repository',
        'dirs': ['.'],
        'url': 'url',
        'username': 'username',
        'password': 'password',
    }],
    [
        'repository -d d1 d2',
        {
            'repository': 'repository',
            'dirs': ['d1', 'd2'],
            'url': 'url',
            'username': 'username',
            'password': 'password',
        }
    ],
])
def test_parse_args_valid(args, expected):
    with patch.dict(environ, {
        'NEXUS3_REST_URL': 'url',
        'NEXUS3_USERNAME': 'username',
        'NEXUS3_PASSWORD': 'password',
    }, clear=True):
        assert expected == parse_args(args.split(' ') if args else '').__dict__
