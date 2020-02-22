from os import environ

work_dir = './work_dir'
# Spec of the artifactory instance to copy from
from_artifactory_spec = {
    'url': environ['ARTIFACTORY_REST_URL'],
    'username': environ['ARTIFACTORY_USERNAME'],
    'password': environ['ARTIFACTORY_PASSWORD'],
}
# Spec of the artifactory instance to copy to
# In example below, by creating a copy of from_artifactory_spec with a different url
to_artifactory_spec = dict(from_artifactory_spec, url='<to_artifactory_url>')

# Specify a pair (tuple) if the repo key to mirror to is not the same as the repo key to mirror from
repositories = [
    ('from_repo_key1', 'to_repo_key1'),
    'from_and_to_repo_key1',
]


# This function is used to filter out files from mirroring
def is_excluded(repo_uri, artifact_spec):
    if artifact_spec['folder']:
        return True
    if artifact_spec['uri'].startswith('/.index/'):
        return True
    if artifact_spec['uri'].endswith('maven-metadata.xml'):
        return True
    if artifact_spec['uri'].endswith('tar'):
        return True
    if artifact_spec['uri'].endswith('war'):
        return True
    if artifact_spec['uri'].endswith('zip'):
        return True
    return False
