#!/usr/bin/env python3
import argparse
from filecmp import cmp
from os import makedirs, remove, walk
from os.path import exists
from shutil import copyfile, rmtree
from sys import argv


def synchronize_dirs(source_dir, dest_dir, ignore_sub_paths=('/.git',)):
    """
    Makes dest_dir look exactly as as source_dir with exception of ignore_sub_paths
    :param source_dir: path as string
    :param dest_dir: path as string
    :param ignore_sub_paths: ignored sub paths as list of string
    :return: List describing synchronizations done
    """
    syncs = []

    # Copy files from source_dir to dest_dir
    for path, dirs, files in walk(source_dir):
        sub_path = path[len(source_dir):]
        if not any([sub_path.startswith(ignore) for ignore in ignore_sub_paths]):
            dest_path = dest_dir + sub_path
            makedirs(dest_path, exist_ok=True)
            for file in files:
                source_file = f'{path}/{file}'
                dest_file = f'{dest_path}/{file}'
                if exists(dest_file):
                    if not cmp(source_file, dest_file):
                        # print('Copying', source_file, 'to', dest_file)
                        copyfile(source_file, dest_file)
                        syncs.append(f'Updated from {source_file} to {dest_file}')
                        print(syncs[-1])
                else:
                    copyfile(source_file, dest_file)
                    syncs.append(f'Added from {source_file} to {dest_file}')
                    print(syncs[-1])

    # Remove files from dest_dir not in dest_dir
    for path, dirs, files in walk(dest_dir):
        sub_path = path[len(dest_dir):]
        if not any([sub_path.startswith(ignore) for ignore in ignore_sub_paths]):
            source_path = source_dir + sub_path
            if not exists(source_path):
                # print('Removing dir', path)
                rmtree(path)
                syncs.append(f'Removed dir {path}')
                print(syncs[-1])
            else:
                for file in files:
                    source_file = f'{source_path}/{file}'
                    dest_file = f'{path}/{file}'
                    if not exists(source_file):
                        # print('Removing file', dest_file)
                        remove(dest_file)
                        syncs.append(f'Removed file {dest_file}')
                        print(syncs[-1])

    return syncs


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Makes dest_dir look exactly as as source_dir with exception of ignore_sub_paths')
    parser.add_argument('source_dir', help='path as string')
    parser.add_argument('dest_dir', help='path as string')
    parser.add_argument('-i', '--ignore_sub_paths', nargs='+', help='ignored sub paths as list of string',
                        default=['/.git'])
    return parser.parse_args(args)


if __name__ == '__main__':
    pargs = parse_args(argv[1:])
    synchronize_dirs(pargs.source_dir, pargs.dest_dir, pargs.ignore_sub_paths)
