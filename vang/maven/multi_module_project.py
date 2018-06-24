#!/usr/bin/env python3

""" Makes Maven multi module project. """

from os import makedirs
from os.path import realpath, relpath, dirname, normpath

import vang.maven.pom as pom

POM_TEMPLATE = """<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>###group_id###</groupId>
    <artifactId>###artifact_id###</artifactId>
    <version>###version###</version>
    <packaging>pom</packaging>
    <modules>
###modules###
    </modules>
</project>"""


def get_pom(pom_infos, output_dir, group_id, artifact_id, version):
    """ Returns multi module pom content for pom_infos with paths relative to output_dir. """
    modules = '\n'.join(
        '        <module>{}</module>'.format(relpath(realpath(dirname(info['pom_path'])), realpath(output_dir)))
        for info in pom_infos)
    return POM_TEMPLATE \
        .replace('###group_id###', group_id) \
        .replace('###artifact_id###', artifact_id) \
        .replace('###version###', version) \
        .replace('###modules###', modules)


def make_project(pom_infos, output_dir, group_id, artifact_id, version, **kwargs):
    """ Makes a Maven multi module project. """
    pom = get_pom(pom_infos, output_dir, group_id, artifact_id, version)
    makedirs(output_dir)
    with open(normpath('{}/pom.xml'.format(output_dir)), 'wt', encoding='utf-8') as pom_file:
        pom_file.write(pom)


def get_pom_infos(source_dir):
    pom_infos = []
    for pom_path in pom.get_pom_paths(source_dir):
        try:
            pom_info = pom.get_pom_info(pom_path)
            pom_infos.append(pom_info)
        except Exception as e:
            print('Can not add {}'.format(pom_path))
            print(e)
    return pom_infos


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create Maven multi module project')
    parser.add_argument('-d', '--defaults', action='store_true', help='Create with default values.')
    args = parser.parse_args()

    defaults = {
        'group_id': 'mygroup',
        'artifact_id': 'ws',
        'version': '1.0.0-SNAPSHOT',
        'source_dir': '.',
        'output_dir': './ws'
    }
    if args.defaults:
        pom_infos = get_pom_infos(defaults['source_dir'])
        make_project(pom_infos, **defaults)
    else:
        group_id = str(input('groupId (default mygroup): ') or defaults['group_id'])
        artifact_id = str(input('artifactId (default ws): ') or defaults['artifact_id'])
        version = str(input('version (default 1.0.0-SNAPSHOT): ') or defaults['version'])
        source_dir = normpath(str(input('sourceDir: (default .)') or defaults['source_dir']))
        output_dir = normpath(str(input('outputDir: (default ./ws)') or defaults['output_dir']))

        pom_infos = get_pom_infos(source_dir)
        make_project(pom_infos, output_dir, group_id, artifact_id, version)


if __name__ == '__main__':
    main()
