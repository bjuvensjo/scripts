#!/usr/bin/env python3

from os import environ

from requests import delete, get, post, put


def call(
        uri,
        request_data=None,
        method='GET',
        only_response_code=False,
        rest_url=environ.get('BITBUCKET_REST_URL', None),
        username=environ.get('BITBUCKET_USERNAME', None),
        password=environ.get('BITBUCKET_PASSWORD', None),
        verify_certificate=not environ.get('BITBUCKET_IGNORE_CERTIFICATE', None),
):
    """Makes a REST call to Bitbucket rest api 1.0.
    Depends on three environment variables:
    * BITBUCKET_REST_URL, e.g. http://myorg.com/stash
    * BITBUCKET_USERNAME, the bitbucket username
    * BITBUCKET_PASSWORD, the bitbucket password

    Args:
        uri (str): e.g. "/rest/api/1.0/projects/{project}/repos/{repo}/branches?filterText={branch}"
        request_data (dict): the JSON request
        method (str): http method
        only_response_code (bool): default False
        rest_url: default environ.get('BITBUCKET_REST_URL', None)
        username (str): default environ.get('BITBUCKET_USERNAME', None)
        password (str): default environ.get('BITBUCKET_PASSWORD', None)
        verify_certificate: True if https certificate should be verified

    Return:
          the JSON response
    """

    m = {'DELETE': delete,
         'GET': get,
         'POST': post,
         'PUT': put,
         }[method]

    params = {'url': f'{rest_url}{uri}', 'auth': (username, password), 'verify': verify_certificate}
    if request_data:
        params['json'] = request_data

    response = m(**params)
    return response.status_code if only_response_code else response.json() if response.text else response.status_code()
