#!/usr/bin/env python3
import traceback
from json import load
from re import match

from os import makedirs

from bb_get_clone_urls import get_clone_urls
from bb_has_branch import has_branch
from shell import run_commands


def has_match(s, regexps):
    return any((match(regexp, s) for regexp in regexps))


def is_excluded(repo_name, excludes):
    return has_match(repo_name, excludes)


def is_included(repo_name, includes):
    return not includes or has_match(repo_name, includes)


def should_be_cloned(project, repo, project_config, has_branch_map):
    return has_branch_map[(project, repo)] \
           and is_included(repo, project_config['includes']) \
           and not is_excluded(repo, project_config['excludes'])


def clone(commands, root_dir):
    makedirs(root_dir, exist_ok=True)
    yield from run_commands([(cmd, root_dir) for cmd in commands], max_processes=25, timeout=20)


def get_projects_commands(projects, branch=None):
    return ((clone_dir, project, repo, command)
            for clone_dir, project, repo, command in get_clone_urls(projects, True, branch))


def get_repos_commands(repos, branch=None):
    projects = {repo.split('/')[0] for repo in repos}
    return ((clone_dir, project, repo, command)
            for clone_dir, project, repo, command in get_clone_urls(projects, True, branch)
            for repo_spec in repos
            if repo_spec == '{}/{}'.format(project, repo))


def get_config_commands(config, branch=None):
    clone_url_specs = tuple(get_clone_urls(config['projects'], True, branch if branch else config['branch']))
    has_branch_specs = has_branch([(p, r) for d, p, r, c in clone_url_specs], config['branch'])
    has_branch_map = {repo_spec: has for repo_spec, has in has_branch_specs}

    return ((clone_dir, project, repo, command) for clone_dir, project, repo, command in clone_url_specs
            if should_be_cloned(project, repo, config['projects'][project], has_branch_map))


def main(root_dir, projects=None, repos=None, config=None, branch=None):
    n = 1
    if projects:
        commands = get_projects_commands(projects, branch)
    elif repos:
        commands = get_repos_commands(repos, branch)
    else:
        with open(config, 'rt', encoding='utf-8') as cfg:
            commands = get_config_commands(load(cfg), branch)

    for process in clone((command for clone_dir, project, repo, command in commands), root_dir):
        try:
            print(str(n).zfill(2), process.stdout.read().decode(), end='')
            n += 1
        except:
            print(traceback.format_exc())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clone Bitbucket repos')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--projects', nargs='+', help='Bitbucket projects, e.g key1 key2')
    group.add_argument('-r', '--repos', nargs='+', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument('-c', '--config', help='Configuration file, see bb_clone_repos.json')
    parser.add_argument('-b', '--branch', help='The clone branch. Overrides branch in configuration file (-c)')
    parser.add_argument('-d', '--dir', default='.', help='The directory to clone into')
    args = parser.parse_args()

    main(args.dir, args.projects, args.repos, args.config, args.branch)
