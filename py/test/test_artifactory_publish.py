import unittest
from unittest.mock import patch, mock_open

from artifactory_publish import *


class ArtifactoryPublish(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'Nobody inspects the spammish repetition')
    def test_read_file(self, mock_file):
        self.assertEqual(b'Nobody inspects the spammish repetition', read_file('file_path'))
        mock_file.assert_called_with('file_path', 'rb')

    def test_get_checksums(self):
        md5, sha1, sha256 = get_checksums(b'Nobody inspects the spammish repetition')
        self.assertEqual('bb649c83dd1ea5c9d9dec9a18df0ffe9', md5)
        self.assertEqual('531b07a0f5b66477a21742d2827176264f4bbfe2', sha1)
        self.assertEqual('031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406', sha256)

    def test_get_checksum_headers(self):
        self.assertEqual({'X-Checksum-Md5': 5, 'X-Checksum-Sha1': 1, 'X-Checksum-Sha256': 256},
                         get_checksum_headers(5, 1, 256))

    @patch('artifactory_publish.glob')
    @patch('artifactory_publish.exists')
    def test_get_pom_path(self, mock_exists, mock_glob):
        mock_exists.return_value = True
        self.assertEqual('/foo/bar/pom.xml', get_pom_path('/foo/bar'))
        mock_exists.assert_called_with('/foo/bar/pom.xml')

        mock_exists.return_value = False
        mock_glob.return_value = ['/foo/bar/foo.pom']
        self.assertEqual('/foo/bar/foo.pom', get_pom_path('/foo/bar'))

        mock_glob.return_value = [
            '/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-20150610.210152-141.pom',
            '/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom']
        self.assertEqual('/signing.updatesigning/1.0.0-SNAPSHOT/signing.updatesigning-1.0.0-SNAPSHOT.pom',
                         get_pom_path('/signing.updatesigning/1.0.0-SNAPSHOT'))

        mock_glob.return_value = []
        self.assertRaises(ValueError, get_pom_path, '/foo/bar')

    def test_get_artifact_base_uri(self):
        self.assertEqual('/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT',
                         get_artifact_base_uri('repo', 'com.foo.bar', 'business.baz', '1.0.0-SNAPSHOT'))

    def test_get_pom_publish_name(self):
        self.assertEqual('business.baz-1.0.0-SNAPSHOT.pom',
                         get_pom_publish_name('/foo/bar/business.baz-1.0.0-SNAPSHOT.pom', 'business.baz',
                                              '1.0.0-SNAPSHOT'))
        self.assertEqual('business.baz-1.0.0-SNAPSHOT.pom',
                         get_pom_publish_name('/foo/bar/pom.xml', 'business.baz', '1.0.0-SNAPSHOT'))

    @patch('artifactory_publish.get_checksum_headers')
    @patch('artifactory_publish.get_checksums')
    @patch('artifactory_publish.read_file')
    def test_get_publish_data(self, mock_read_file, mock_get_checksums, mock_get_checksum_headers):
        mock_read_file.return_value = b'Hello World!'
        mock_get_checksums.return_value = [5, 1, 256]
        mock_get_checksum_headers.return_value = {'X-Checksum-Md5': 5, 'X-Checksum-Sha1': 1, 'X-Checksum-Sha256': 256}
        self.assertEqual({'checksum_headers': {'X-Checksum-Md5': 5,
                                               'X-Checksum-Sha1': 1,
                                               'X-Checksum-Sha256': 256},
                          'content': b'Hello World!',
                          'uri': '/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT/business.baz-1.0.0-SNAPSHOT.pom'},
                         get_publish_data('/repo/com/foo/bar/business.baz/1.0.0-SNAPSHOT',
                                          '/foo/bar/foo.pom',
                                          'business.baz-1.0.0-SNAPSHOT.pom'))


if __name__ == '__main__':
    unittest.main()
