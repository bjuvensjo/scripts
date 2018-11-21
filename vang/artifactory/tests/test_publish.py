from unittest.mock import patch, mock_open

from vang.artifactory.publish import get_checksum_headers
from vang.artifactory.publish import get_checksums
from vang.artifactory.publish import get_pom_publish_name
from vang.artifactory.publish import get_publish_data
from vang.artifactory.publish import main
from vang.artifactory.publish import parse_args
from vang.artifactory.publish import publish_maven_artifact
from vang.artifactory.publish import read_file

import pytest


@patch(
    'builtins.open',
    new_callable=mock_open,
    read_data=b'Nobody inspects the spammish repetition')
def test_read_file(mock_file):
    assert b'Nobody inspects the spammish repetition' == read_file('file_path')
    mock_file.assert_called_with('file_path', 'rb')


def test_get_checksums():
    md5, sha1, sha256 = get_checksums(
        b'Nobody inspects the spammish repetition')
    assert 'bb649c83dd1ea5c9d9dec9a18df0ffe9' == md5
    assert '531b07a0f5b66477a21742d2827176264f4bbfe2' == sha1
    assert '031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406' == sha256


def test_get_checksum_headers():
    assert {
        'X-Checksum-Md5': 5,
        'X-Checksum-Sha1': 1,
        'X-Checksum-Sha256': 256
    } == get_checksum_headers(5, 1, 256)


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


@patch('vang.artifactory.publish.get_checksum_headers')
@patch('vang.artifactory.publish.get_checksums')
@patch('vang.artifactory.publish.read_file')
def test_get_publish_data(
        mock_read_file,
        mock_get_checksums,
        mock_get_checksum_headers,
):
    mock_read_file.return_value = b'Hello World!'
    mock_get_checksums.return_value = [5, 1, 256]
    mock_get_checksum_headers.return_value = {
        'X-Checksum-Md5': 5,
        'X-Checksum-Sha1': 1,
        'X-Checksum-Sha256': 256
    }
    assert {
        'checksum_headers': {
            'X-Checksum-Md5': 5,
            'X-Checksum-Sha1': 1,
            'X-Checksum-Sha256': 256
        },
        'content':
        b'Hello World!',
        'uri':
        '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT/business.baz-1.0.0-SNAPSHOT.pom'
    } == get_publish_data(
        '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT',
        '/foo/bar/foo.pom',
        'business.baz-1.0.0-SNAPSHOT.pom',
    )
