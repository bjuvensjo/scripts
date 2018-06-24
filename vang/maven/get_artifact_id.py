#!/usr/bin/env python3

from os import name, system

from vang.maven.pom import get_pom_info


def get_artifact_id(pom_path):
    return get_pom_info(pom_path)['artifact_id']


def main():
    artifact_id = get_artifact_id('./pom.xml')
    if name == 'posix':
        system('echo "{}\c" | pbcopy'.format(artifact_id))
        print('"{}" copied to clipboard'.format(artifact_id))
    else:
        print(artifact_id)


if __name__ == '__main__':
    main()
