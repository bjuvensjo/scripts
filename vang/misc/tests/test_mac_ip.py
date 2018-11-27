from unittest.mock import call, patch

from vang.misc.mac_ip import main


@patch('vang.misc.mac_ip.print')
@patch('vang.misc.mac_ip.system', autospec=True)
@patch('vang.misc.mac_ip.get_ip_address', autospec=True)
def test_main(mock_get_ip_address, mock_system, mock_print):
    mock_get_ip_address.return_value = '1.2.3.4'

    main()

    assert [call('echo "1.2.3.4\\c" | pbcopy')] == mock_system.mock_calls

    assert [call('1.2.3.4')] == mock_print.mock_calls
