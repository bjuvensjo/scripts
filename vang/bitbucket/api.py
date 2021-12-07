#!/usr/bin/env python3
import sys
from os import environ

from requests import delete, get, post, put


def get_page(uri, params, limit, start):
    query = f"&{'&'.join([f'{k}={v}' for k, v in params.items()])}" if params else ''
    response = call(f'{uri}?limit={limit}&start={start}{query}')
    return response['size'], response['values'], response[
        'isLastPage'], response.get('nextPageStart', -1)


def get_all(uri, params=None, take=sys.maxsize):
    limit = min(take, 1000)
    start = 0
    is_last_page = False

    result = []
    while not is_last_page and len(result) < take:
        size, values, is_last_page, start = get_page(uri, params, limit, start)

        if size:
            result += values
    return result[:take]


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
    # print(username, password, rest_url, request_data, uri)
    params = {'url': f'{rest_url}{uri}', 'auth': (username, password), 'verify': verify_certificate}
    if request_data:
        params['json'] = request_data

    response = m(**params)
    return response.status_code if only_response_code else response.json() if response.text else response.status_code()
