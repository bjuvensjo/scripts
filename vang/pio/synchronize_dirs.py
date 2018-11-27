#!/usr/bin/env python3
import argparse
from filecmp import cmp
from os import makedirs, remove, walk
from os.path import exists
from shutil import copyfile, rmtree
from sys import argv


def add(dest_dir, ignore_sub_paths, source_dir):
    adds = []
    for path, dirs, files in walk(source_dir):
        sub_path = path[len(source_dir):]
        if not any([sub_path.startswith(ignore)
                    for ignore in ignore_sub_paths]):
            dest_path = dest_dir + sub_path
            makedirs(dest_path, exist_ok=True)
            for file in files:
                source_file = f'{path}/{file}'
                dest_file = f'{dest_path}/{file}'
                if exists(dest_file):
                    if not cmp(source_file, dest_file):
                        copyfile(source_file, dest_file)
                        adds.append(
                            f'Updated from {source_file} to {dest_file}')
                        print(adds[-1])
                else:
                    copyfile(source_file, dest_file)
                    adds.append(f'Added from {source_file} to {dest_file}')
                    print(adds[-1])
    return adds


def delete(dest_dir, ignore_sub_paths, source_dir):
    deletes = []
    for path, dirs, files in walk(dest_dir):
        sub_path = path[len(dest_dir):]
        if not any([sub_path.startswith(ignore)
                    for ignore in ignore_sub_paths]):
            source_path = source_dir + sub_path
            if not exists(source_path):
                rmtree(path)
                deletes.append(f'Removed dir {path}')
                print(deletes[-1])
            else:
                for file in files:
                    source_file = f'{source_path}/{file}'
                    dest_file = f'{path}/{file}'
                    if not exists(source_file):
                        remove(dest_file)
                        deletes.append(f'Removed file {dest_file}')
                        print(deletes[-1])
    return deletes


def synchronize_dirs(source_dir, dest_dir, ignore_sub_paths=('/.git', )):
    """
    Makes dest_dir look exactly as as source_dir
    with exception of ignore_sub_paths
    :param source_dir: path as string
    :param dest_dir: path as string
    :param ignore_sub_paths: ignored sub paths as list of string
    :return: List describing synchronizations done
    """
    adds = add(dest_dir, ignore_sub_paths, source_dir)
    deletes = delete(dest_dir, ignore_sub_paths, source_dir)
    return adds + deletes


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Makes dest_dir look exactly as as source_dir '
        'with exception of ignore_sub_paths')
    parser.add_argument('source_dir', help='path as string')
    parser.add_argument('dest_dir', help='path as string')
    parser.add_argument(
        '-i',
        '--ignore_sub_paths',
        nargs='+',
        help='ignored sub paths as list of string',
        default=['/.git'])
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    synchronize_dirs(**parse_args(argv[1:]).__dict__)
