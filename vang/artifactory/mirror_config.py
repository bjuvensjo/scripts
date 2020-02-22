work_dir = './work_dir'
from_artifactory_url = 'e.g. http://my_org/old_artifactory'
from_artifactory_username = '<username>'
from_artifactory_password = '<password>'
to_artifactory_url = 'e.g. http://my_org/new_artifactory'
to_artifactory_username = '<username>'
to_artifactory_password = '<password'

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
