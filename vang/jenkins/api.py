#!/usr/bin/env python3

from os import environ

from requests import delete, get, post, put


def call(
        uri,
        request_data=None,
        method='GET',
        only_response_code=False,
        rest_url=environ.get('JENKINS_REST_URL', None),
        username=environ.get('JENKINS_USERNAME', None),
        password=environ.get('JENKINS_PASSWORD', None),
        verify_certificate=not environ.get('JENKINS_IGNORE_CERTIFICATE', None),
):
    """Makes a REST call to Jenkins rest api.
    May use three environment variables:
    * JENKINS_REST_URL, e.g. http://myorg.com/stash
    * JENKINS_USERNAME, the jenkins username
    * JENKINS_PASSWORD, the jenkins password

    Args:
        uri (str): e.g. "/api/json"
        request_data (dict): the JSON request
        method: http method
        only_response_code: default False
        rest_url: default environ.get('JENKINS_REST_URL', None)
        username: default environ.get('JENKINS_USERNAME', None)
        password: default environ.get('JENKINS_PASSWORD', None)
        verify_certificate: True if https certificate should be verified

    Return:
          the response
    """
    return call_url(f'{rest_url}{uri}', request_data, method, only_response_code, username, password,
                    verify_certificate)


def call_url(
        url,
        request_data=None,
        method='GET',
        only_response_code=False,
        username=environ.get('JENKINS_USERNAME', None),
        password=environ.get('JENKINS_PASSWORD', None),
        verify_certificate=True,
):
    m = {'DELETE': delete,
         'GET': get,
         'POST': post,
         'PUT': put,
         }[method]

    params = {'url': url, 'auth': (username, password), 'verify': verify_certificate}
    if request_data:
        params['json'] = request_data

    response = m(**params)
    return response.status_code if only_response_code else response.json() if response.text else response.status_code()
