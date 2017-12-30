#!/usr/bin/env python3
import re

from sys import argv

from bb_get_clone_urls import get_all_clone_urls
from bb_get_projects import get_all_projects


def get_clone_urls_grep(pattern):
    return get_all_clone_urls([p['key'] for p in get_all_projects() if re.match(pattern, p['key'])])


if __name__ == '__main__':
    for project, repo, clone_url, in get_clone_urls_grep(argv[1]):
        clone_dir = '{}/{}'.format(project, repo.replace('.', '/'))
        print('git clone {} {}'.format(clone_url, clone_dir))
