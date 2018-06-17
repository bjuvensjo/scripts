#!/usr/bin/env python3
from argparse import ArgumentParser
from re import compile
from sys import argv


def get_split(s):
    for ch in ('_', '-'):
        if ch in s:
            return s.split(ch)
    return compile('[A-Z]?[^A-Z]+').findall(s)


def get_cases(s):
    split = get_split(s)
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
        '-'.join(upper),
    ]


def get_zipped_cases(strings):
    return zip(*[get_cases(s) for s in strings])


def parse_args(args):
    parser = ArgumentParser(
        description='Prints various string representation of provided strings')
    parser.add_argument('strings', nargs='+')
    return parser.parse_args(args)


def main(strings):
    for items in get_zipped_cases(strings):
        print(' '.join(items))


if __name__ == '__main__':
    main(parse_args(argv[1:]).strings)
