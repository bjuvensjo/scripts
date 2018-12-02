#!/usr/bin/env python3
import argparse
from glob import glob
from os import environ, makedirs, remove
from os.path import exists, normpath, realpath
from shutil import rmtree
from sys import argv
from traceback import print_exc

from vang.pio.shell import run_command


def get_jars(root):
    return [realpath(p) for p in
            glob(normpath(f'{root}/**/*.jar'), recursive=True)]


def print_release_info(release_info, develop_branch, release_branch,
                       release_tag):
    content = release_info.split("\n")
    if develop_branch:
        print(content[0])
    if release_branch:
        print(content[1])
    if release_tag:
        print(content[2])


def get_release_info(war, develop_branch, release_branch, release_tag):
    work_dir = environ['HOME'] + '/tmp_wildcat'
    try:
        release_info = 'META-INF/release.info'
        release_info_path = f'{work_dir}/{release_info}'
        makedirs(work_dir)
        run_command(f'jar xvf {realpath(war)}', cwd=work_dir,
                    return_output=True)
        with open(f'{work_dir}/WEB-INF/classes/{release_info}', 'rt',
                  encoding='utf-8') as f:
            print_release_info(f.read(), develop_branch, release_branch,
                               release_tag)

        for jar in get_jars(work_dir):
            if exists(release_info_path):
                remove(release_info_path)
            run_command(f'jar xvf {jar} -x {release_info}', cwd=work_dir,
                        return_output=True)
            if exists(release_info_path):
                with open(release_info_path, 'rt', encoding='utf-8') as f:
                    print_release_info(f.read(), develop_branch, release_branch,
                                       release_tag)
    except OSError:
        print_exc()
    finally:
        rmtree(work_dir, ignore_errors=True)


def main(war, develop_branch, release_branch, release_tag):
    get_release_info(war, develop_branch, release_branch, release_tag)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Print release.info of all artifacts in war')
    parser.add_argument('war', help='The war file')
    parser.add_argument('-d', '--develop_branch',
                        help='Print clone commands of develop_branch',
                        action='store_true')
    parser.add_argument('-r', '--release_branch',
                        help='Print clone commands of release_branch',
                        action='store_true')
    parser.add_argument('-t', '--release_tag',
                        help='Print clone commands of release_tag',
                        action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':  # pragma: no cover
    pargs = parse_args(argv[1:])
    params = [pargs.develop_branch, pargs.release_branch, pargs.release_tag]
    main(pargs.war, *params if any(params) else [True, True, True])
