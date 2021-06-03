#!/usr/bin/env python3
import socket
from os import system


def get_ip_address():  # pragma: no cover
    """
    Returns the ip address.
    """
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


def main():
    ip_address = get_ip_address()
    system(f'echo "{ip_address}\\c" | pbcopy')
    print(ip_address)


if __name__ == '__main__':  # pragma: no cover
    main()
