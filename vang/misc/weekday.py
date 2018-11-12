#!/usr/bin/env python3
from sys import argv


def name(d):
    return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][d - 1]


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


if __name__ == '__main__':
    a_year = int(argv[1])
    a_month = int(argv[2])
    a_day = int(argv[3])

    print(name(zeller(a_year, a_month, a_day)))
