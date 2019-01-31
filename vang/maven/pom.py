#!/usr/bin/env python3
""" Maven pom utilities. """

from glob import glob
from os.path import realpath, normpath
from xml.etree.ElementTree import parse

NAME_SPACES = {'ns': 'http://maven.apache.org/POM/4.0.0'}


def get_pom_paths(root):
    """ Returns the absolute path of poms that recursively are found in root"""
    return [realpath(p) for p in glob(f"{root}/**/pom.xml", recursive=True)]


def get_pom_info(pom_path):
    """ Returns a dictionary with pom_path, artifact_id,
    group_id, version and packaging. """
    e = parse(normpath(pom_path))
    info = {
        'pom_path': pom_path,
        'artifact_id': e.findtext('ns:artifactId', namespaces=NAME_SPACES) or e.findtext('artifactId'),
        'group_id': e.findtext('ns:groupId', namespaces=NAME_SPACES) or e.findtext('groupId'),
        'version': e.findtext('ns:version', namespaces=NAME_SPACES)  or e.findtext('version'),
        'packaging': e.findtext('ns:packaging', namespaces=NAME_SPACES) or e.findtext('packaging') or 'jar'
    }
    if not info['group_id']:
        info['group_id'] = e.findtext('ns:parent/ns:groupId', namespaces=NAME_SPACES) or e.findtext('parent/groupId')
    if not info['version']:
        info['version'] = e.findtext('ns:parent/ns:version', namespaces=NAME_SPACES) or e.findtext('parent/version')

    return info
