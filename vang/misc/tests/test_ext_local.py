from unittest.mock import call, mock_open, patch

from pytest import raises

from vang.misc.ext_local import main
from vang.misc.ext_local import parse_args
from vang.misc.ext_local import update

import pytest


@pytest.fixture
def expected_hosts():
    return [
        "##\n",
        "# Host Database\n",
        "#\n",
        "# localhost is used to configure the loopback interface\n",
        "# when the system is booting.  Do not change this entry.\n",
        "##\n",
        "127.0.0.1       localhost\n",
        "255.255.255.255 broadcasthost\n",
        "::1             localhost\n",
        "100.100.1.100   ext.local\n",
    ]


@pytest.mark.parametrize(
    "hosts, backup_file",
    [
        (
            "\n".join(
                [
                    "##",
                    "# Host Database",
                    "#",
                    "# localhost is used to configure the loopback interface",
                    "# when the system is booting.  Do not change this entry.",
                    "##",
                    "127.0.0.1       localhost",
                    "255.255.255.255 broadcasthost",
                    "::1             localhost",
                ]
            ),
            None,
        ),
        (
            "\n".join(
                [
                    "##",
                    "# Host Database",
                    "#",
                    "# localhost is used to configure the loopback interface",
                    "# when the system is booting.  Do not change this entry.",
                    "##",
                    "127.0.0.1       localhost",
                    "255.255.255.255 broadcasthost",
                    "::1             localhost\n",
                ]
            ),
            None,
        ),
        (
            "\n".join(
                [
                    "##",
                    "# Host Database",
                    "#",
                    "# localhost is used to configure the loopback interface",
                    "# when the system is booting.  Do not change this entry.",
                    "##",
                    "127.0.0.1       localhost",
                    "255.255.255.255 broadcasthost",
                    "::1             localhost",
                    "187.168.1.179   ext.local\n",
                ]
            ),
            "backup_file",
        ),
    ],
)
@patch("vang.misc.ext_local.get_ip_address", autospec=True)
@patch("vang.misc.ext_local.copy2", autospec=True)
def test_update(
    mock_copy2,
    mock_get_ip_address,
    hosts,
    backup_file,
    expected_hosts,
):
    mock_get_ip_address.return_value = "100.100.1.100"
    with patch("vang.misc.ext_local.open", new_callable=mock_open, read_data=hosts):
        assert update(backup_file) == expected_hosts
        if backup_file:
            assert mock_copy2.mock_calls == [call("/etc/hosts", "backup_file")]


@pytest.mark.parametrize(
    "args",
    [
        "1",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            "",
            {"backup": None},
        ),
        (
            "-b b",
            {"backup": "b"},
        ),
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected


@patch("vang.misc.ext_local.print")
@patch("vang.misc.ext_local.update", autospec=True)
def test_main(mock_update, mock_print):
    mock_update.return_value = ["foo\n", "bar"]
    main("backup")
    assert mock_update.mock_calls == [call("backup")]
    assert mock_print.mock_calls == [call("foo\nbar")]
