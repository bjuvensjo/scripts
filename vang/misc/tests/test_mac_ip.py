from unittest.mock import call, patch

from vang.misc.mac_ip import mac_ip


@patch("vang.misc.mac_ip.print")
@patch("vang.misc.mac_ip.system", autospec=True)
@patch("vang.misc.mac_ip.get_ip_address", autospec=True)
def test_mac_ip(mock_get_ip_address, mock_system, mock_print):
    mock_get_ip_address.return_value = "1.2.3.4"
    mac_ip()
    assert mock_system.mock_calls == [call('echo "1.2.3.4\\c" | pbcopy')]
    assert mock_print.mock_calls == [call("1.2.3.4")]
