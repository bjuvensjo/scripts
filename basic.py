#!/usr/bin/env python3

from base64 import encodebytes
from os import environ, name, system
from sys import argv


def get_basic_auth(username=environ['U'], password=environ['P']):
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


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    basic_auth = get_basic_auth(argv[1], argv[2]) if len(argv) == 3 else get_basic_auth()
    basic_auth_header = f"Authorization: {basic_auth}"

    if name == 'posix':
        system(f"echo '{basic_auth_header}\c' | pbcopy")
        print(f"'{basic_auth_header}' copied to clipboard")
    else:
        print(basic_auth_header)
