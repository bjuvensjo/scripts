#!/usr/bin/env python3

from os import environ

from requests import delete, get, post, put


def call(
        uri,
        request_data=None,
        method='GET',
        only_response_code=False,
        rest_url=environ.get('TFS_REST_URL', None),
        token=environ.get('TFS_TOKEN', None),
):
    """Makes a REST call to TFS rest api.
    May use three environment variables:
    * TFS_REST_URL, e.g. http://myorg.com/stash
    * TFS_TOKEN, the tfs token

    Args:
        uri (str): e.g. "{organisation}/{project}/_apis/build/definitions/{definition_id}?api-version=3.2"
        request_data (dict): the JSON request
        method: http method
        only_response_code: default False
        rest_url: default environ.get('TFS_REST_URL', None)
        token: default environ.get('TFS_TOKEN', None),

    Return:
          the JSON response
    """
    return call_url(f'{rest_url}{uri}', request_data, method, only_response_code, token)


def call_url(
        url,
        request_data=None,
        method='GET',
        only_response_code=False,
        token=environ.get('TFS_TOKEN', None),
        verify_certificate=False,
):
    """Makes a REST call to TFS rest api.
    May use three environment variables:
    * TFS_TOKEN, the tfs token

    Args:
        url (str): e.g. "http://myorg:8080/tfs/{organisation}/{project}/_apis/build/definitions/{definition_id}?api-version=3.2"
        request_data (dict): the JSON request
        method: http method
        only_response_code: default False
        token: default environ.get('TFS_TOKEN', None),
        verify_certificate: True if https certificate should be verified,

    Return:
          the JSON response
    """
    m = {'DELETE': delete,
         'GET': get,
         'POST': post,
         'PUT': put,
         }[method]

    params = {'url': url, 'auth': ('', token), 'verify': verify_certificate}
    if request_data:
        params['json'] = request_data

    response = m(**params)
    return response.status_code if only_response_code else response.json() if response.text else response.status_code()
