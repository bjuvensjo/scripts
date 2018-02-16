#!/usr/bin/env python3
from glob import glob
from os import makedirs, remove, environ
from os.path import realpath, normpath, exists
from shutil import rmtree
from traceback import print_exc

from shell import run_command


def get_jars(root):
    return [realpath(p) for p in glob(normpath('{}/**/{}'.format(root, '*.jar')), recursive=True)]


def get_release_info(war):
    try:
        work_dir = environ['HOME'] + '/tmp_wildcat'
        release_info = 'META-INF/release.info'
        release_info_path = '{}/{}'.format(work_dir, release_info)
        makedirs(work_dir)
        run_command('jar xvf {}'.format(realpath(war)), cwd=work_dir, return_output=True)
        with open('{}/WEB-INF/classes/{}'.format(work_dir, release_info), 'rt', encoding='utf-8') as f:
            print(war.split('/')[-1], f.read(), end='')

        for jar in get_jars(work_dir):
            if exists(release_info_path):
                remove(release_info_path)
            run_command('jar xvf {} -x {}'.format(jar, release_info), cwd=work_dir, return_output=True)
            if exists(release_info_path):
                with open(release_info_path, 'rt', encoding='utf-8') as f:
                    print(jar.split('/')[-1], f.read(), end='')
    except:
        print_exc()
    finally:
        rmtree(work_dir, ignore_errors=True)


def main(war):
    get_release_info(war)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Print release.info of all artifacts in war')
    parser.add_argument('war', help='The war file')
    args = parser.parse_args()

    main(args.war)
