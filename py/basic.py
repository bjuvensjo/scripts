#!/usr/bin/env python3

from base64 import encodebytes
from os import environ, name, system


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


def main(username, password):
    basic_auth = get_basic_auth(username, password)
    basic_auth_header = f"Authorization: {basic_auth}"
    if name == 'posix':
        system(f"echo '{basic_auth_header}\c' | pbcopy")
        print(f"'{basic_auth_header}' copied to clipboard")
    else:
        print(basic_auth_header)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Prints and place in clipboard basic authentication header')
    parser.add_argument('-u', '--username', help='Username', default=environ['U'])
    parser.add_argument('-p', '--password', help='Psssword', default=environ['P'])
    args = parser.parse_args()

    main(args.username, args.password)
