#!/usr/bin/env python3
from base64 import encodebytes
from json import loads
from os import environ
from urllib.request import Request, urlopen


def call(uri,
         extra_headers=None,
         request_data=None,
         method='GET',
         rest_url=environ.get('ARTIFACTORY_REST_URL', None),
         username=environ.get('ARTIFACTORY_USERNAME', None),
         password=environ.get('ARTIFACTORY_PASSWORD', None)):
    """Makes a REST call to Artifactory.

    Args:
        uri (str): e.g. "/{repository/{'/'.join(group_id.split('.'))}/{artifact_id}/{version}""
        extra_headers: default None
        request_data (bytes): the request payload
        method (str): http method
        rest_url: artifactory rest url
        username: artifactory username
        password: artifactory password

    Return:
          the JSON response (dict)
    """
    auth = f'{username}:{password}'
    basic_auth_header = f'Basic {encodebytes(auth.encode()).decode("UTF-8").strip()}'
    url = f'{rest_url}{uri}'
    headers = {
        'Authorization': basic_auth_header,
        'Content-Type': 'application/json'
    }
    if extra_headers:
        headers.update(extra_headers)

    request = create_request(headers, method, request_data, url)
    response = urlopen(request)
    response_data = response.read()
    return loads(
        response_data.decode('UTF-8')) if response_data else response.getcode()


def create_request(headers, method, request_data, url):
    return Request(
        url, request_data if request_data else None, headers, method=method)
