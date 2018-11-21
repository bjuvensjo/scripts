#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv


def name(d):
    return [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ][d - 1]


def zeller(year, month, day):
    """ Calculates the weekday.

    :param year: e.g. 2018
    :param month: 1..12
    :param day: 1..31
    :return: the ISO week date Day-of-Week d (1 = Monday to 7 = Sunday)
    """
    y = year - 1 if month < 3 else year
    q = day
    m = month + 12 if month < 3 else month
    k = y % 100
    j = y // 100

    h = (q + 13 * (m + 1) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
    return ((h + 5) % 7) + 1


def parse_args(args):
    parser = ArgumentParser(description='Prints weekday')
    parser.add_argument('year', help='Year')
    parser.add_argument('month', help='Month')
    parser.add_argument('day', help='Day')
    return parser.parse_args(args)


def main(year, month, day):
    print(name(zeller(int(year), int(month), int(day))))


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
