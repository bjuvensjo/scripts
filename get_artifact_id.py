#!/usr/bin/env python3

import xml.etree.ElementTree as ET

from os import name, system


def get_artifact_id(pom):
    root = ET.parse(pom).getroot()
    return next(child for child in root if child.tag.split('}')[-1] == 'artifactId').text


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    artifact_id = get_artifact_id('./pom.xml')

    if name == 'posix':
        system('echo "{}\c" | pbcopy'.format(artifact_id))
        print('"{}" copied to clipboard'.format(artifact_id))
    else:
        print(artifact_id)
