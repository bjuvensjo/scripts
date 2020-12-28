from unittest.mock import call, patch

from vang.maven.get_artifact_id import get_artifact_id
from vang.maven.get_artifact_id import main


def test_get_artifact_id():
    with patch(
            'vang.maven.get_artifact_id.get_pom_info',
            return_value={'artifact_id': 'artifact_id'}) as m:
        assert 'artifact_id' == get_artifact_id('pom_path')
        m.assert_called_with('pom_path')


def test_main():
    with patch(
            'vang.maven.get_artifact_id.get_artifact_id',
            return_value='artifact_id'):
        with patch('vang.maven.get_artifact_id.name', 'posix'):
            with patch('vang.maven.get_artifact_id.system') as mock_system:
                with patch('builtins.print') as mock_print:
                    main()
                    assert [call('echo "artifact_id\\c" | pbcopy')
                            ] == mock_system.mock_calls
                    assert [call('"artifact_id" copied to clipboard')
                            ] == mock_print.mock_calls
        with patch('vang.maven.get_artifact_id.name', 'not-posix'):
            with patch('builtins.print') as mock_print:
                main()
                assert [call('artifact_id')] == mock_print.mock_calls
