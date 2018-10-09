#!/usr/bin/env python3
from argparse import ArgumentParser
from base64 import encodebytes
from os import environ, name, system
from sys import argv

from vang.pio.shell import run_command


def get_ip_address():
    rc, output = run_command('ipconfig getifaddr en0', return_output=True)
    return output


if __name__ == '__main__':
    ip_address = get_ip_address()
    system(f'echo "{ip_address}\c" | pbcopy')
    print(ip_address)
