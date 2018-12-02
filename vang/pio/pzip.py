#!/usr/bin/env python3
import argparse
from datetime import datetime
from fnmatch import fnmatch
from json import dumps, loads
from os import makedirs
from os import walk
from os.path import dirname, relpath
from sys import argv
from zipfile import ZipFile


def create_zip(the_entries, output_file):
    makedirs(dirname(output_file), exist_ok=True)

    the_zip_file = output_file.replace('#timestamp#',
                                       datetime.now().strftime('%Y%m%dT%H%M%S'))
    with ZipFile(the_zip_file, 'w') as z:
        for base_path, rel_path, flatten in the_entries:
            file_name = f'{base_path}/{rel_path}'
            arc_name = rel_path.split('/')[-1] if flatten else rel_path
            z.write(file_name, arc_name)
    return the_zip_file


def has_match(name, patterns):
    return any([fnmatch(name, pattern) for pattern in patterns])


def get_patterns(key, default, **kwargs):
    if key not in kwargs:
        return default
    return [p.split('->')[0] for p in kwargs[key]]


def is_included(dir_path, file_name, path):
    rel_path = relpath(f'{dir_path}/{file_name}', path)
    return has_match('includes',
                     get_patterns('includes', ['.*'])) and not has_match(
        rel_path, get_patterns('excludes', []))


def get_entries(dirs):
    return [
        (d['path'], relpath(f'{dir_path}/{file_name}', d['path']), d['flatten'])
        for d in dirs
        for dir_path, dir_names, file_names in walk(d['path'])
        for file_name in file_names
        if is_included(dir_path, file_name, d['path'])]


def load_config(config):
    with open(config, 'rt', encoding='utf-8') as cfg:
        return loads(cfg.read())


def pzip(config):
    cfg = load_config(config)
    the_entries = get_entries(cfg['dirs'])
    the_zip_file = create_zip(the_entries, cfg['output_file'])
    return the_zip_file, the_entries


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Zip as configured in specified config file.')
    parser.add_argument('config', help=dumps({
        "dirs": [
            {
                "path": "/Users/me/.m2/repository/release/com/foo/bar",
                "flatten": True,
                "includes": [
                    "business*/**/*.jar",
                    "war.es/1.0.1-SNAPSHOT/war.es-1.0.1-SNAPSHOT.war"
                ],
                "excludes": [
                    "**/*javadoc*",
                    "**/*sources*"
                ]
            }
        ],
        "output_file": "./releases/release-#timestamp#.zip"
    }))
    return parser.parse_args(args)


def main(config):
    zip_file, entries = pzip(config)
    print(f'Zip file: {zip_file}')


if __name__ == '__main__':  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
