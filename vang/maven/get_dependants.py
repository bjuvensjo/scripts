#!/usr/bin/env python3

import argparse
from pprint import pprint
from re import search
from sys import argv


def get_dependants(dependency_tree_file, dependency):
    dependency_dict = {}
    with open(dependency_tree_file, 'rt') as file:
        previous_line = ''
        artifact = None
        for line in file.readlines():
            if previous_line.startswith('[INFO] --- maven-dependency-plugin'):
                artifact = line.split(' ')[1].strip()
            elif line.strip() == '[INFO]':
                artifact = None
            elif artifact and search(r'{}'.format(dependency), line):
                key = line.rsplit(' ', maxsplit=1)[1].strip()
                dependants = dependency_dict.get(key, {'direct': set(), 'transitive': set()})
                dependency_dict[key] = dependants
                dependants['transitive' if '|' in line else 'direct'].add(artifact)
            previous_line = line
    return dependency_dict


def main(dependency_tree_file, dependency, only_direct, only_transitive):
    dependants = get_dependants(dependency_tree_file, dependency)
    key = 'direct' if only_direct else 'transitive' if only_transitive else None

    if key:
        d = {}
        for k, v in dependants.items():
            d[k] = v[key]
        dependants = d

    pprint(dependants)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get direct and transitive dependants from provided dependency_tree_file, '
                    'e.g. ./get_dependants.py ./dependency_tree.txt org.slf4j:slf4j-api')
    parser.add_argument('dependency_tree_file',
                        help='Dependency tree file (created with e.g. mvn dependency:tree > dependency_tree.txt')
    parser.add_argument('dependency', help='The dependency to analyse, e.g. logback. '
                        'Can be a fully qualified dependency, e.g. org.slf4j:slf4j-api:jar:1.7.7:compile, '
                        'or a substring of a dependency, e.g. slf4j-api:jar:1.7.7, '
                        'or a quoted regular expression substring, e.g. "slf4j.*1.7.7".')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-d', '--only_direct', help='Print only direct dependants', action='store_true')
    group.add_argument(
        '-t', '--only_transitive', help='Print only transitive dependants', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
