#!/usr/bin/env python3
import argparse
import hashlib
from itertools import count
from os import walk
from os.path import exists
from re import match
from sys import argv


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def diff(master_dir, compare_dir, ignore):
    """
    Returns files in master dir that are not in compare_dir,
    and file in master dir that differ (sha256) from files in compare_dir

    :param master_dir:
    :param compare_dir:
    :param ignore:
    :return:
    """
    missing_files = []
    diffing_files = []

    for root, dirs, files in walk(master_dir):
        for f in files:
            if not any([match(p, f) for p in ignore]):
                mf = f'{root}/{f}'
                cf = f'{compare_dir}/{root[len(master_dir) + 1:]}/{f}'

                if exists(cf):
                    if sha256sum(mf) != sha256sum(cf):
                        diffing_files.append((mf, cf))
                else:
                    missing_files.append(mf)

    return missing_files, diffing_files


def main(master_dir, compare_dir, ignore, only_files=False):
    mfs, dfs = diff(master_dir, compare_dir, ignore)

    if only_files:
        for mf in mfs:
            print(mf)
        for mf, df in dfs:
            print(mf)
    else:
        print('##### Missing files #####')
        for n, mf in zip(count(), mfs):
            print(n, mf)

        print('##### Diffing files #####')
        for n, df in zip(count(), dfs):
            print(n, df)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Returns files in master dir that are not '
                    'in compare_dir, and file in master dir that differ '
                    '(sha256) from files in compare_dir')
    parser.add_argument('master_dir', help='master dir')
    parser.add_argument('compare_dir', help='compare dir')
    parser.add_argument(
        '-i',
        '--ignore',
        nargs='*',
        default=(
            r'.*lastUpdated',
            r'_remote.repositories',
            r'.*sha1',
            r'maven-metadata-local.xml',
            r'maven-metadata-local.xml',
        ))
    parser.add_argument(
        '-f',
        '--only_files',
        action='store_true'
    )
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
