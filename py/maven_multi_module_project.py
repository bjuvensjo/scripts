#!/usr/bin/env python3

""" Makes Maven multi module project. """

from os import makedirs
from os.path import realpath, relpath, dirname

import maven_pom

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


def make_project(output_dir, group_id, artifact_id, version, source_dir):
    """ Makes a Maven multi module project. """
    pom_info = [maven_pom.get_pom_info(pom_path) for pom_path in maven_pom.get_pom_paths(source_dir)]
    pom = get_pom(pom_info, output_dir, group_id, artifact_id, version)
    makedirs(output_dir)
    with open('{}/pom.xml'.format(output_dir), 'wt', encoding='utf-8') as pom_file:
        pom_file.write(pom)


def main():
    group_id = str(input('groupId (default mygroup): ') or 'mygroup')
    artifact_id = str(input('artifactId (default ws): ') or 'ws')
    version = str(input('version (default 1.0.0-SNAPSHOT): ') or '1.0.0-SNAPSHOT')
    source_dir = str(input('sourceDir: (default .)') or '.')
    output_dir = str(input('outputDir: (default ./ws)') or './ws')
    make_project(output_dir, group_id, artifact_id, version, source_dir)


if __name__ == '__main__':
    main()
