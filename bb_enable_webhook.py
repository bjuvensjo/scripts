#!/usr/bin/env python3

from sys import argv

import bb_api
from bb_utils import get_clone_url, get_project_and_repo


def _get_uri(project, repo):
    return f"projects/{project}/repos/{repo}" + \
           "/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled"


def enable_web_hook(repo_specs):
    for spec in repo_specs:
        uri = _get_uri(spec[0], spec[1])
        request_data = '{"hook-url-0":"http://10.46.64.31:8000/cgi-bin/webhook/"}'.encode('UTF-8')
        yield spec, bb_api.call(uri, request_data, "PUT")


if __name__ == "__main__":
    dirs = "." if len(argv) < 2 else argv[1:]

    specs = [get_project_and_repo(get_clone_url(dir)) for dir in dirs]

    for spec, response in enable_web_hook(specs):
        print(f"{spec[0]}/{spec[1]}: {'enabled' if response['enabled'] else ' not enabled'}")
