#!/usr/bin/env python3
from argparse import ArgumentParser
from base64 import encodebytes
from os import name, system
from sys import argv


def get_basic_auth(username, password):
    """Returns basic authentication.

    Args:
        username (str): the username (defaults to environment variable 'U')
        password (str): the password (defaults to environment variable 'P')

    Return:
          base 64 encoded Authorization header value

    >>> get_basic_auth("foo", "bar")
    'Basic Zm9vOmJhcg=='
    """

    auth = f"{username}:{password}"
    return f"Basic {encodebytes(auth.encode()).decode('UTF-8').strip()}"


def get_basic_auth_header(username, password):
    return f"Authorization: {get_basic_auth(username, password)}"


def parse_args(args):
    parser = ArgumentParser(
        description="Prints and place in clipboard basic authentication header"
    )
    parser.add_argument("username", help="Username")
    parser.add_argument("password", help="Password")
    return parser.parse_args(args)


def basic(username, password):
    basic_auth_header = get_basic_auth_header(username, password)
    if name == "posix":
        system(f"echo '{basic_auth_header}\\c' | pbcopy")
        print(f"'{basic_auth_header}' copied to clipboard")
    else:
        print(basic_auth_header)


def main() -> None:  # pragma: no cover
    basic(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
