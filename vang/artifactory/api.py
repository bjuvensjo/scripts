#!/usr/bin/env python3
from base64 import encodebytes
from json import loads
from os import environ
from urllib.request import Request, urlopen


def call(uri, extra_headers=None, request_data=None, method='GET'):
    """Makes a REST call to Artifactory.
    Depends on three environment variables:
    * ARTIFACTORY_REST_API_URL, e.g. http://myorg.com/artifactory
    * U, the artifactory username
    * P, the artifactory password

    Args:
        uri (str): e.g. "/{repository/{'/'.join(group_id.split('.'))}/{artifact_id}/{version}""
        request_data (bytes): the request payload
        method (str): http method

    Return:
          the JSON response (dict)
    """
    auth = '{}:{}'.format(environ['U'], environ['P'])
    basic_auth_header = 'Basic {}'.format(
        encodebytes(auth.encode()).decode('UTF-8').strip())
    url = '{}{}'.format(environ['ARTIFACTORY_REST_API_URL'], uri)
    headers = {
        'Authorization': basic_auth_header,
        'Content-Type': 'application/json'
    }
    if extra_headers:
        headers.update(extra_headers)

    request = Request(
        url, request_data if request_data else None, headers, method=method)
    response = urlopen(request)
    response_data = response.read()
    return loads(
        response_data.decode('UTF-8')) if response_data else response.getcode()
