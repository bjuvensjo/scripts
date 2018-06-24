#!/usr/bin/env python3
import argparse
import traceback
from json import load
from os import makedirs
from sys import argv

from vang.bitbucket.get_clone_urls import get_clone_urls
from vang.bitbucket.has_branch import has_branch
from vang.core.core import is_included
from vang.pio.shell import run_commands


def should_be_cloned(project, repo, project_config, has_branch_map):
    return has_branch_map[(project, repo)] and is_included(
        repo,
        project_config['excludes'],
        project_config['includes'],
    )


def clone(commands, root_dir):
    makedirs(root_dir, exist_ok=True)
    yield from run_commands(
        [(cmd, root_dir) for cmd in commands],
        max_processes=25,
        timeout=30,
        check=False)


def get_projects_commands(projects, branch=None, flat=False):
    return ((clone_dir, project, repo, command)
            for clone_dir, project, repo, command in get_clone_urls(
                projects, True, branch, flat))


def get_repos_commands(repos, branch=None, flat=False):
    projects = {repo.split('/')[0] for repo in repos}

    commands = []
    clone_urls_map = {
        '{}/{}'.format(project, repo): (clone_dir, project, repo, command)
        for clone_dir, project, repo, command in get_clone_urls(
            projects, True, branch, flat)
    }
    for repo_spec in repos:
        if repo_spec in clone_urls_map:
            commands.append(clone_urls_map[repo_spec])
        else:
            print('Warning! Non existing repo: {}'.format(repo_spec))

    return commands


def get_config_commands(config, branch=None, flat=False):
    clone_url_specs = tuple(
        get_clone_urls(config['projects'], True, branch
                       if branch else config['branch'], flat))
    has_branch_specs = has_branch([(p, r) for d, p, r, c in clone_url_specs],
                                  config['branch'])
    has_branch_map = {repo_spec: has for repo_spec, has in has_branch_specs}

    return ((clone_dir, project, repo, command)
            for clone_dir, project, repo, command in clone_url_specs
            if should_be_cloned(project, repo, config['projects'][project],
                                has_branch_map))


def main(root_dir,
         projects=None,
         repos=None,
         config=None,
         branch=None,
         flat=False):
    n = 1
    if projects:
        commands = get_projects_commands(projects, branch, flat)
    elif repos:
        commands = get_repos_commands(repos, branch, flat)
    else:
        with open(config, 'rt', encoding='utf-8') as cfg:
            commands = get_config_commands(load(cfg), branch, flat)

    for process in clone(
        [command for clone_dir, project, repo, command in commands],
            root_dir,
    ):
        try:
            print(str(n).zfill(2), process.stdout.decode(), end='')
            n += 1
        except OSError:
            print(traceback.format_exc())


def parse_args(args):
    parser = argparse.ArgumentParser(description='Clone Bitbucket repos')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-p', '--projects', nargs='+', help='Bitbucket projects, e.g key1 key2')
    group.add_argument(
        '-r', '--repos', nargs='+', help='Repos, e.g. key1/repo1 key2/repo2')
    group.add_argument(
        '-c', '--config', help='Configuration file, see clone_repos.json')
    parser.add_argument(
        '-b',
        '--branch',
        help='The clone branch. Overrides branch in configuration file (-c)')
    parser.add_argument(
        '-d', '--dir', default='.', help='The directory to clone into')
    parser.add_argument(
        '-f', '--flat', help='Clone to flat structure', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.dir, args.projects, args.repos, args.config, args.branch,
         args.flat)
