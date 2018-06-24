#!/usr/bin/env python3
from glob import glob
from os import makedirs, remove, environ
from os.path import realpath, normpath, exists
from shutil import rmtree
from traceback import print_exc

from vang.pio.shell import run_command


def get_jars(root):
    return [realpath(p) for p in glob(normpath('{}/**/{}'.format(root, '*.jar')), recursive=True)]


def print_release_info(release_info, develop_branch, release_branch, release_tag):
    content = release_info.split("\n")
    if develop_branch:
        print(content[0])
    if release_branch:
        print(content[1])
    if release_tag:
        print(content[2])


def get_release_info(war, develop_branch, release_branch, release_tag):
    try:
        work_dir = environ['HOME'] + '/tmp_wildcat'
        release_info = 'META-INF/release.info'
        release_info_path = '{}/{}'.format(work_dir, release_info)
        makedirs(work_dir)
        run_command('jar xvf {}'.format(realpath(war)), cwd=work_dir, return_output=True)
        with open('{}/WEB-INF/classes/{}'.format(work_dir, release_info), 'rt', encoding='utf-8') as f:
            print_release_info(f.read(), develop_branch, release_branch, release_tag)

        for jar in get_jars(work_dir):
            if exists(release_info_path):
                remove(release_info_path)
            run_command('jar xvf {} -x {}'.format(jar, release_info), cwd=work_dir, return_output=True)
            if exists(release_info_path):
                with open(release_info_path, 'rt', encoding='utf-8') as f:
                    print_release_info(f.read(), develop_branch, release_branch, release_tag)
    except:
        print_exc()
    finally:
        rmtree(work_dir, ignore_errors=True)


def main(war, develop_branch, release_branch, release_tag):
    get_release_info(war, develop_branch, release_branch, release_tag)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Print release.info of all artifacts in war')
    parser.add_argument('war', help='The war file')
    parser.add_argument('-d', '--develop_branch', help='Print clone commands of develop_branch', action='store_true')
    parser.add_argument('-r', '--release_branch', help='Print clone commands of release_branch', action='store_true')
    parser.add_argument('-t', '--release_tag', help='Print clone commands of release_tag', action='store_true')
    args = parser.parse_args()

    params = [args.develop_branch, args.release_branch, args.release_tag]
    main(args.war, *params if any(params) else [True, True, True])
