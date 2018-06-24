#!/usr/bin/env python3
from datetime import datetime
from fnmatch import fnmatch
from json import loads, dumps
from os import makedirs
from os import walk
from os.path import dirname, relpath
from zipfile import ZipFile


def zip(entries, output_file):
    makedirs(dirname(output_file), exist_ok=True)

    zip_file = output_file.replace('#timestamp#', datetime.now().strftime('%Y%m%dT%H%M%S'))
    with ZipFile(zip_file, 'w') as z:
        for base_path, rel_path, flatten in entries:
            file_name = '{}/{}'.format(base_path, rel_path)
            arc_name = rel_path.split('/')[-1] if flatten else rel_path
            z.write(file_name, arc_name)
    return zip_file


def has_match(name, patterns):
    return any([fnmatch(name, pattern) for pattern in patterns])


def get_patterns(key, default, **kwargs):
    if not key in kwargs:
        return default
    return [p.split('->')[0] for p in kwargs[key]]


def is_included(dir_path, file_name, path, **kwargs):
    rel_path = relpath('{}/{}'.format(dir_path, file_name), path)
    return has_match('includes', get_patterns('includes', ['.*'], kwargs)) and \
           not has_match(rel_path, get_patterns('excludes', [], kwargs))


def get_entries(dirs):
    return [(d['path'], relpath('{}/{}'.format(dir_path, file_name), d['path']), d['flatten'])
            for d in dirs
            for dir_path, dir_names, file_names in walk(d['path'])
            for file_name in file_names
            if is_included(dir_path, file_name, **d)]


def load_config(config):
    with open(config, 'rt', encoding='utf-8') as cfg:
        return loads(cfg.read())


def pzip(config):
    cfg = load_config(config)
    entries = get_entries(cfg['dirs'])
    zip_file = zip(entries, cfg['output_file'])
    return zip_file, entries


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Zip as configured in specified config file.')
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
    args = parser.parse_args()

    zip_file, entries = pzip(args.config)
    print('Zip file: {}'.format(zip_file))
