#!/usr/bin/env python3

from base64 import encodebytes
from json import loads
from os import environ
from urllib.request import Request, urlopen


def call(uri, request_data=None, method="GET"):
    api_url = "http://cuso.edb.se/stash/rest/api/1.0"
    auth = f"{environ['U']}:{environ['P']}"
    basic_auth_header = f"Basic {encodebytes(auth.encode()).decode('UTF-8').strip()}"
    url = f"{api_url}/{uri}"

    request = Request(url,
                      request_data,
                      {
                          "Authorization": basic_auth_header,
                          "Content-Type": "application/json"
                      },
                      method=method)

    response = urlopen(request)
    response_data = response.read()
    return loads(response_data.decode('UTF-8')) if response_data else response.getcode()
