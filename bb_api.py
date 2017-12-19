#!/usr/bin/env python3

from base64 import encodebytes
from json import loads
from os import environ
from urllib.request import Request, urlopen


def call(uri, request_data=None, method="GET"):
    """Makes a REST call to Bitbucket rest api 1.0.
    Depends on three environment variables:
    * BB_REST_API_URL, e.g. http://myorg.com/stash
    * U, the bitbucket username
    * P, the bitbucket password

    Args: 
        uri (str): e.g. "/rest/api/1.0/projects/{project}/repos/{repo}/branches?filterText={branch}"
        request_data (str): the JSON request
        method: http method

    Return:
          the JSON response
    """
    auth = '{}:{}'.format(environ['U'], environ['P'])
    basic_auth_header = 'Basic {}'.format(encodebytes(auth.encode()).decode('UTF-8').strip())
    url = '{}{}'.format(environ['BB_REST_API_URL'], uri)

    request = Request(url,
                      request_data.encode("UTF-8") if request_data else None,
                      {
                          'Authorization': basic_auth_header,
                          'Content-Type': "application/json"
                      },
                      method=method)

    response = urlopen(request)
    response_data = response.read()
    return loads(response_data.decode('UTF-8')) if response_data else response.getcode()


if __name__ == '__main__':
    import doctest

    doctest.testmod()
