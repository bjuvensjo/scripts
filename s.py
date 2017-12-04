#!/usr/bin/env python3

from re import compile
from sys import argv


def get_cases(s):
    split = compile('[A-Z]?[^A-Z]+').findall(s)
    capital = [w.capitalize() for w in split]
    lower = [w.lower() for w in split]
    upper = [w.upper() for w in split]
    return '\n'.join([
        ''.join([lower[0]] + capital[1:]),
        ''.join(capital),
        ''.join(lower),
        ''.join(upper),
        '_'.join(lower),
        '_'.join(upper),
        '-'.join(lower),
        '-'.join(upper)
    ])


if __name__ == "__main__":
    print(get_cases(argv[1]))
