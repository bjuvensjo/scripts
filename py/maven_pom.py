#!/usr/bin/env python3

""" Maven pom utilities. """

from glob import glob
from os.path import realpath, normpath
from xml.etree.ElementTree import parse

NAME_SPACES = {'ns': 'http://maven.apache.org/POM/4.0.0'}


def get_pom_paths(root):
    """ Returns the absolute path of the poms that recursively is found in root"""
    return [realpath(p) for p in glob("{}/**/pom.xml".format(root), recursive=True)]


def get_pom_info(pom_path):
    """ Returns a dictionary with pom_path, artifact_id, group_id, version and packaging. """
    e = parse(normpath(pom_path))
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
