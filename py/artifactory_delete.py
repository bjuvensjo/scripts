#!/usr/bin/env python3
from os.path import basename

from sys import argv

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
        # yield base_uri
        yield api.call(base_uri, method='DELETE')


if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: {} artifactory_repository [pom_dirs]'.format(basename(__file__)))
    else:
        artifactory_repository = argv[1]
        pom_dirs = argv[2:] if len(argv) > 2 else ['.']
        for response in delete_maven_artifact(artifactory_repository, pom_dirs):
            print(response)
            # print(json.dumps(json.loads(str(response).replace("'", '"')), indent=2))
