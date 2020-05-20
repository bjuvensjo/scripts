from vang.artifactory.mirror import not_folders, not_index, not_maven_metadata, latest_version

work_dir = './work_dir'
# Spec of the artifactory instance to copy from
from_artifactory_spec = {
    'url': '<from_artifactory_url>',
    'username': '<username>',
    'password': '<password>',
}
# Spec of the artifactory instance to copy to
# In example below, by creating a copy of from_artifactory_spec with a different url
to_artifactory_spec = dict(from_artifactory_spec, url='<to_artifactory_url>')

# Specify a pair (tuple) if the repo key to mirror to is not the same as the repo key to mirror from
repositories = [
    ('from_repo_key', 'to_repo_key'),
    'from_and_to_repo_key'
]

filters = (not_folders, not_index, not_maven_metadata, latest_version)
