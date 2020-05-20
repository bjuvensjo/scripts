from unittest.mock import patch, mock_open

from vang.nexus3.upload import read_file


@patch(
    'builtins.open',
    new_callable=mock_open,
    read_data=b'Nobody inspects the spammish repetition')
def test_read_file(mock_file):
    assert b'Nobody inspects the spammish repetition' == read_file('file_path')
    mock_file.assert_called_with('file_path', 'rb')
