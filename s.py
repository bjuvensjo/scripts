#!/usr/bin/env python3

from re import compile
from sys import argv


def get_cases(s):
    split = compile('[A-Z]?[^A-Z]+').findall(s)
    capital = [w.capitalize() for w in split]
    lower = [w.lower() for w in split]
    upper = [w.upper() for w in split]
    return [
        ''.join([lower[0]] + capital[1:]),
        ''.join(capital),
        ''.join(lower),
        ''.join(upper),
        '_'.join(lower),
        '_'.join(upper),
        '-'.join(lower),
        '-'.join(upper)
    ]


def get_zipped_cases(strings):
    return zip(*[get_cases(s) for s in strings])


if __name__ == "__main__":
    print(get_zipped_cases(argv[1:]))
    for items in get_zipped_cases(argv[1:]):
        print(' '.join(items))
