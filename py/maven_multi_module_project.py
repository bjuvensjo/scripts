#!/usr/bin/env python3

from glob import glob
from os import makedirs
from os.path import realpath, relpath, dirname
from xml.etree.ElementTree import parse

NAME_SPACES = {'ns': 'http://maven.apache.org/POM/4.0.0'}
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


def get_pom_paths(root):
    """ Returns the absolute path of the poms that recursively is found in root"""
    return [realpath(p) for p in glob("{}/**/pom.xml".format(root), recursive=True)]


def get_pom_info(pom_path):
    """ Returns a dictionary with pom_path, artifact_id, group_id, version and packaging. """
    e = parse(pom_path)
    info = {
        'pom_path': pom_path,
        'artifact_id': e.findtext('ns:artifactId', namespaces=NAME_SPACES),
        'group_id': e.findtext('ns:groupId', namespaces=NAME_SPACES),
        'version': e.findtext('ns:version', namespaces=NAME_SPACES),
        'packaging': e.findtext('ns:packaging', namespaces=NAME_SPACES)
    }
    if not info['group_id']:
        info['group_id'] = e.findtext('ns:parent/ns:groupId', namespaces=NAME_SPACES)
    if not info['version']:
        info['version'] = e.findtext('ns:parent/ns:version', namespaces=NAME_SPACES)

    return info


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
    pom_info = [get_pom_info(pom_path) for pom_path in get_pom_paths(source_dir)]
    pom = get_pom(pom_info, output_dir, group_id, artifact_id, version)
    makedirs(output_dir)
    with open('{}/pom.xml'.format(output_dir), 'wt', encoding='utf-8') as pom_file:
        pom_file.write(pom)


if __name__ == '__main__':
    group_id = str(input('groupId (default mygroup): ') or 'mygroup')
    artifact_id = str(input('artifactId (default ws): ') or 'ws')
    version = str(input('version (default 1.0.0-SNAPSHOT): ') or '1.0.0-SNAPSHOT')
    source_dir = str(input('sourceDir: (default .)') or '.')
    output_dir = str(input('outputDir: (default ./ws)') or './ws')

    make_project(output_dir, group_id, artifact_id, version, source_dir)
