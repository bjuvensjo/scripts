#!/usr/bin/env python3

from json import loads
from os import environ
from base64 import encodebytes
from pprint import pprint as pp
import subprocess
import sys
import urllib.request

api_url = "http://cuso.edb.se/stash/rest/api/1.0"

def get_clone_url(git_dir):
    completed_process = subprocess.run(f"git --git-dir {git_dir} remote get-url origin".split(), 
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed_process.returncode:
        completed_process = subprocess.run(f"git --git-dir {git_dir + '/.git'} remote get-url origin".split(), 
                                           universal_newlines=True, stdout=subprocess.PIPE)

    return completed_process.stdout.strip()


def get_basic_auth_header(username, password):
    auth = f"{username}:{password}"
    return f"Basic {encodebytes(auth.encode()).decode('UTF-8').strip()}"


def enable_web_hook(git_dirs):
    for git_dir in git_dirs:
        clone_url = get_clone_url(git_dir)
        project = clone_url.split('/')[-2].upper()
        repo = '.'.join(clone_url.split('/')[-1].split('.')[:-1])
        url=f"{api_url}/projects/{project}/repos/{repo}" + \
             "/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled"
        request_data='{"hook-url-0":"http://10.46.64.31:8000/cgi-bin/webhook/"}'.encode('UTF-8')
        request = urllib.request.Request(url, 
                                         request_data, 
                                         {
                                             "Authorization": get_basic_auth_header(environ['U'], environ['P']),
                                             "Content-Type": "application/json"
                                         },
                                         method="PUT")

        reponse_data = urllib.request.urlopen(request).read()
        response =  loads(reponse_data.decode('UTF-8'))

        print(clone_url + ' enabled' if response['enabled'] else ' not enabled')


if __name__ == "__main__":
    enable_web_hook(sys.argv[1:])
