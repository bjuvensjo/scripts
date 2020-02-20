#!/usr/bin/env python3
from os import environ

from vang.jenkins.copy_jobs import copy_jobs

# This script can be used to copy jobs between Jenkins instances, possibly with modifications.
# With a minor modification, it can also be used to update jobs on a Jenkins instance.

# Can be an iterable with pairs of old and new, or a function
# that takes the from_job configuration as parameter and returns the updated configuration.
# Will be used if no job specific replacement has been specified.
replacements = [
    ('old_foo', 'new_foo'),
    ('old_bar', 'new_bar'),
]

# An iterable with strings and/or
# a pair of strings with job names and/or
# a pair of string with job names and job specific replacements (see replacements).
#
# If only a string, the name of from_job and to_job will be the same.
# If a pair of strings, the first element is the name of the from_job and the second will be the name of the clone_job,
# i.e. this can be used to rename the clone.
# A third element can be used to specify job specific replacements, i.e. it overrides the default replacements.
jobs = [
    ('from_job_1', 'to_job_1'),
    ('from_job_2', 'to_job_2', lambda x: x),
    ('from_job_3', 'to_job_3', [('old_baz', 'new_baz')])
]

# Spec of the Jenkins instance to copy from
from_jenkins_spec = {
    'url': environ.get('JENKINS_REST_URL', None),
    'username': environ['JENKINS_USERNAME'],
    'password': environ['JENKINS_PASSWORD'],
    'verify_certificate': not environ.get('JENKINS_IGNORE_CERTIFICATE', None),
}

# Spec of the Jenkins instance to copy to
to_jenkins_spec = dict(from_jenkins_spec, url='<to_jenkins_url>')

# Call the copy_jobs function to perform the actual replacement
copy_jobs(jobs, from_jenkins_spec, to_jenkins_spec, replacements)
