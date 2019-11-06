#!/usr/bin/env python3
import argparse
import logging
import re
from sys import argv, stdout

from vang.pio.shell import run_command

logging.basicConfig(stream=stdout, level=logging.INFO)


def get_dependencies(dependency_tree_split):
    lines = dependency_tree_split.split('\n')
    module = lines[0].replace('[INFO]', '').strip()
    direct = []
    transitive = []
    for line in lines[1:]:
        if line.startswith('[INFO] +- ') or line.startswith('[INFO] \- '):
            direct.append(line.split('-', maxsplit=1)[1].strip())
        else:
            transitive.append(line.split('-', maxsplit=1)[1].strip())
    return module, sorted(direct), sorted(transitive)


def split_dependency_tree(dependency_tree):
    """Splits a multi module into separate parts and a single module to one."""
    splits = re.split(r'\[INFO\] --- maven-dependency-plugin.*', dependency_tree)
    if len(splits) < 2:
        return []
    modules = []
    for m in splits[1:]:
        lines = []
        for line in m.strip().split('\n'):
            if len(line.split(':')) >= 4:
                lines.append(line)
            else:
                break
        modules.append('\n'.join(lines))

    return modules


def get_dependency_tree(pom_file):
    code, output = run_command(f'mvn dependency:tree -f {pom_file}', True)
    return output


def get_modules_dependencies(pom_file):
    dependency_tree = get_dependency_tree(pom_file)
    logging.debug('dependency tree: %s', dependency_tree)
    modules_dependency_trees = split_dependency_tree(dependency_tree)
    logging.debug('modules dependency tree: %s', modules_dependency_trees)
    modules_dependencies = [get_dependencies(mdt) for mdt in modules_dependency_trees]
    return modules_dependencies


def main(pom_file, only_direct, only_transitive):
    for module, direct, transitive in get_modules_dependencies(pom_file):
        print('#' * 80)
        print(module)
        if not only_transitive:
            print('direct:\n  ', '\n  '.join(direct), sep='')
        if not only_direct:
            print('transitive:\n  ', '\n  '.join(transitive), sep='')
        print('#' * 80)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Get direct and transitive dependencies from provided pom.xml, '
                    'e.g. ./get_dependencies.py ./pom.xml. '
                    'Depends on Maven.')
    parser.add_argument('-p', '--pom_file', help='Path to pom file', default='pom.xml')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-d', '--only_direct', help='Print only direct dependants', action='store_true')
    group.add_argument(
        '-t', '--only_transitive', help='Print only transitive dependants', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
