#!/usr/bin/env python3
import logging
import random
from argparse import ArgumentParser
from random import choice, shuffle
from string import ascii_lowercase, ascii_uppercase, digits
from sys import argv

logging.basicConfig(level=logging.INFO)


def generate_random_password(special_characters: str = '!@#$%^&*()',
                             number_ascii_lower: int = random.randint(7, 8),
                             number_ascii_upper: int = random.randint(3, 4),
                             number_digits: int = random.randint(3, 4),
                             number_special: int = random.randint(3, 4)) -> str:
    password = [choice(c) for c, n in [[digits, number_digits],
                                       [ascii_lowercase, number_ascii_lower],
                                       [ascii_uppercase, number_ascii_upper],
                                       [special_characters, number_special]]
                for i in range(n)]

    shuffle(password)

    logging.info('Password of length %s: %s lowercase letters, %s uppercase letters, %s digits, %s special characters',
                 len(password),
                 number_ascii_lower,
                 number_ascii_upper,
                 number_digits,
                 number_special)

    return ''.join(password)


def parse_args(args):
    parser = ArgumentParser(description='Generates a password. '
                                        'Default 16-20 characters: '
                                        'lowercase and uppercase letters, digits and special characters.')
    parser.add_argument('-s', '--special_characters',
                        help='Special characters to use in password generation')
    parser.add_argument('-nl', '--number_ascii_lower', type=int,
                        help='Number of ascii lowercase letters in the password')
    parser.add_argument('-nu', '--number_ascii_upper', type=int,
                        help='Number of ascii uppercase letters in the password')
    parser.add_argument('-nd', '--number_digits', type=int,
                        help='Number of digits in the password')
    parser.add_argument('-ns', '--number_special', type=int,
                        help='Number of special characters in the password')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = {k: v for (k, v) in parse_args(argv[1:]).__dict__.items() if v}
    print(generate_random_password(**args))
