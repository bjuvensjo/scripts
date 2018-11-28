#!/usr/bin/env python3

from base64 import encodebytes
from json import loads
from os import environ
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def call(
        uri,
        request_data=None,
        method='GET',
        rest_url=environ.get('BITBUCKET_REST_URL', None),
        username=environ.get('BITBUCKET_USERNAME', None),
        password=environ.get('BITBUCKET_PASSWORD', None),
):
    """Makes a REST call to Bitbucket rest api 1.0.
    Depends on three environment variables:
    * BITBUCKET_REST_URL, e.g. http://myorg.com/stash
    * BITBUCKET_USERNAME, the bitbucket username
    * BITBUCKET_PASSWORD, the bitbucket password

    Args:
        uri (str): e.g. "/rest/api/1.0/projects/{project}/repos/{repo}/branches?filterText={branch}"
        request_data (str): the JSON request
        method: http method

    Return:
          the JSON response
    """
    auth = f'{username}:{password}'
    basic_auth_header = f'Basic {encodebytes(auth.encode()).decode("UTF-8").strip()}'
    rest_url = f'{rest_url}{uri}'

    request = create_request(basic_auth_header, method, request_data, rest_url)

    try:
        response = urlopen(request)
        response_data = response.read()
        return loads(response_data.decode(
            'UTF-8')) if response_data else response.getcode()
    except HTTPError as e:  # pragma: no cover
        print(f'Can not call {uri}, {request_data}, {method}, {e}')
        raise e


def create_request(basic_auth_header, method, request_data, url):
    return Request(
        url,
        request_data.encode("UTF-8") if request_data else None, {
            'Authorization': basic_auth_header,
            'Content-Type': "application/json"
        },
        method=method)
