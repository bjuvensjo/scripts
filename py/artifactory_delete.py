#!/usr/bin/env python3

import artifactory_api as api
import artifactory_utils as utils
import maven_pom


def delete_maven_artifact(artifactory_repository, pom_dirs):
    for pom_dir in pom_dirs:
        pom_info = maven_pom.get_pom_info(utils.get_pom_path(pom_dir))
        base_uri = utils.get_artifact_base_uri(artifactory_repository,
                                               pom_info['group_id'],
                                               pom_info['artifact_id'],
                                               pom_info['version'])
        yield api.call(base_uri, method='DELETE')


def main(artifactory_repository, pom_dirs):
    for response in delete_maven_artifact(artifactory_repository, pom_dirs):
        print(response)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Delete maven artifact from Artifactory')
    parser.add_argument('artifactory_repository_url', help='Artifactory repository url')
    parser.add_argument('-d', '--dirs', nargs='*', default=['.'],
                        help='Maven pom directories to extract artifact information from')
    args = parser.parse_args()

    main(args.artifactory_repository_url, args.dirs)
