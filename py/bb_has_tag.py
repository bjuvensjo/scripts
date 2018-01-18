#!/usr/bin/env python3
from bb_get_tags import get_tags
from bb_utils import get_repo_specs


def has_tag(repo_specs, tag):
    for spec, response in get_tags(repo_specs, tag):
        yield spec, tag in [value['displayId'] for value in response['values']]


def main(tag, dirs=['.'], repos=None, projects=None):
    specs = get_repo_specs(dirs, repos, projects)
    for spec, has in has_tag(specs, tag):
        print('{}/{}, {}: {}'.format(spec[0], spec[1], tag, has))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Check repository tags in Bitbucket')
    parser.add_argument('tag', help='The tag to check')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs', nargs='*', default=['.'],
                       help='Git directories to extract repo information from')
    group.add_argument('-r', '--repos', nargs='*', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-p', '--projects', nargs='*',
                       help='Projects, e.g. key1 key2')
    args = parser.parse_args()

    main(args.tag, args.dirs, args.repos, args.projects)
