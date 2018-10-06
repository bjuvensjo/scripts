#!/usr/bin/env python3

from base64 import encodebytes, b64encode
from json import loads
from os import environ
from urllib.error import HTTPError
from urllib.request import Request, urlopen


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
        uri (str): e.g. "/rest/api/1.0/projects/{project}/repos/{repo}/branches?filterText={branch}"
        request_data (str): the JSON request
        method: http method

    Return:
          the JSON response
    """
    auth = f':{token}'
    basic_auth_header = f'Basic {b64encode(auth.encode("utf-8")).decode()}'
    url = f'{rest_url}{uri}'

    request = Request(
        url,
        request_data.encode("UTF-8") if request_data else None,
        {
            'Authorization': basic_auth_header,
            'Content-Type': "application/json"
        },
        method=method,
    )

    try:
        response = urlopen(request)
        response_code = response.getcode()
        if only_response_code:
            return response_code
        response_data = response.read()
        return loads(response_data.decode(
            'UTF-8')) if response_data else response.getcode()
    except HTTPError as e:
        print(f'Can not call {url}, {request_data}, {method}, {e}')
        raise e
