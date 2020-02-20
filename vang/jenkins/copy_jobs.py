#!/usr/bin/env python3

from vang.jenkins.copy_job import copy_job


def copy_jobs(jobs, from_jenkins_spec, to_jenkins_spec, replacements=[], verbose=False):
    for job in jobs:
        from_name = None
        to_name = None
        job_replacements = replacements
        try:
            if type(job) is str:
                to_name = from_name = job
            elif type(jobs) is list and len(job) == 2:
                from_name, to_name = job
            elif type(jobs) is list and len(job) == 3:
                from_name, to_name, job_replacements = job

            if type(from_name) != str or type(to_name) != str or not (
                    type(job_replacements) is list or callable(job_replacements)):
                raise ValueError('job must be a string, a pair of strings or a pair of string and a callable')

            response = copy_job(from_name, to_name, from_jenkins_spec, to_jenkins_spec, job_replacements)
            response_code = response['response_code']
            print('Created copy' if response_code == 200 else 'Failed to create copy', to_name, response_code)
            if verbose:
                print(response)
        except IOError as r:
            print('IOError while trying to create copy', to_name, r)
        except ValueError as v:
            print('ValueError while trying to create copy', to_name, v)
