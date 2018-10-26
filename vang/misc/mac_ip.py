#!/usr/bin/env python3
from os import system

from vang.pio.shell import run_command


def get_ip_address():
    """
    Returns the ip adress.
    """
    rc, output = run_command('ipconfig getifaddr en0', return_output=True)
    return output


if __name__ == '__main__':
    ip_address = get_ip_address()
    system(f'echo "{ip_address}\c" | pbcopy')
    print(ip_address)
