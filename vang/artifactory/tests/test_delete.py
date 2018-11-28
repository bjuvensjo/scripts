from pytest import raises

from unittest.mock import call, patch, mock_open

from vang.artifactory.delete import delete_maven_artifact
from vang.artifactory.delete import main
from vang.artifactory.delete import parse_args

import pytest


@patch('vang.artifactory.delete.api.call')
@patch('vang.artifactory.delete.utils.get_artifact_base_uri')
@patch('vang.artifactory.delete.get_pom_info')
@patch('vang.artifactory.delete.utils.get_pom_path')
def test_delete_maven_artifact(
        mock_get_pom_path,
        mock_get_pom_info,
        mock_get_artifact_base_uri,
        mock_call,
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
    mock_call.return_value = '"response"'

    assert ['"response"', '"response"'] == list(
        delete_maven_artifact('repository', ['d1', 'd2']))


@patch('vang.artifactory.delete.print')
@patch('vang.artifactory.delete.delete_maven_artifact')
def test_main(mock_delete_maven_artifact, mock_print):
    mock_delete_maven_artifact.return_value = ['"response"']
    main('repository', ['d1', 'd2'])
    assert [call('repository',
                 ['d1', 'd2'])] == mock_delete_maven_artifact.mock_calls
    assert [call('"response"')] == mock_print.mock_calls


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
        'pom_dirs': ['.'],
    }],
    [
        'repository -d d1 d2',
        {
            'repository': 'repository',
            'pom_dirs': ['d1', 'd2'],
        }
    ],
])
def test_parse_args_valid(args, expected):
    assert expected == parse_args(args.split(' ') if args else '').__dict__
