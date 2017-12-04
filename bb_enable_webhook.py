#!/usr/bin/env python3

import subprocess
import sys

import bb_api


def _get_clone_url(git_dir):
    completed_process = subprocess.run(f"git --git-dir {git_dir} remote get-url origin".split(),
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed_process.returncode:
        completed_process = subprocess.run(f"git --git-dir {git_dir + '/.git'} remote get-url origin".split(),
                                           universal_newlines=True, stdout=subprocess.PIPE)

    return completed_process.stdout.strip()


def _get_uri(clone_url):
    project = clone_url.split('/')[-2].upper()
    repo = '.'.join(clone_url.split('/')[-1].split('.')[:-1])
    return f"projects/{project}/repos/{repo}" + \
           "/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled"


def enable_web_hook(git_dirs):
    for git_dir in git_dirs:
        clone_url = _get_clone_url(git_dir)
        uri = _get_uri(clone_url)
        request_data = '{"hook-url-0":"http://10.46.64.31:8000/cgi-bin/webhook/"}'.encode('UTF-8')
        yield clone_url, bb_api.call(uri, request_data, "PUT")


if __name__ == "__main__":
    for url, response in enable_web_hook(sys.argv[1:]):
        print(url + ' enabled' if response['enabled'] else ' not enabled')
