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

# def get_cases 

if __name__ == "__main__":
    for items in zip(*[get_cases(s) for s in argv[1:]]):
        print(' '.join(items))

        # print(get_cases(argv[1]))
