#!/usr/bin/env python3

import traceback
from os import getcwd

from vang.bitbucket.clone_repos import clone, get_config_commands
from vang.maven.multi_module_project import make_project
from vang.maven.pom import get_pom_info, get_pom_paths

clone_config = {
    "branch": "develop",
    "projects": {"PSLAS": {"includes": [], "excludes": ["wildcat"]}},
}

mmp_config = {
    "output_dir": "ws",
    "group_id": ".".join(getcwd().split("/")[-2:]),
    "artifact_id": "ws",
    "version": "1.0.0-SNAPSHOT",
}


def get_mmp_args(root_dir):
    return {
        "output_dir": f'{root_dir}/{mmp_config["output_dir"]}',
        "group_id": getcwd().split("/")[-1],
        "artifact_id": "ws",
        "version": "1.0.0-SNAPSHOT",
        "pom_infos": [get_pom_info(pom_path) for pom_path in get_pom_paths(root_dir)],
    }


def do_clone(root_dir, branch="develop"):
    commands = get_config_commands(clone_config, branch)
    n = 1
    for process in clone(
        (command for clone_dir, project, repo, command in commands), root_dir
    ):
        try:
            print(str(n).zfill(2), process.stdout.read().decode(), end="")
            n += 1
        except OSError:
            print(traceback.format_exc())


def do_mmp(root_dir):
    make_project(**get_mmp_args(root_dir))


def clone_config_and_create_mmp(root_dir, branch):
    do_clone(root_dir, branch)
    do_mmp(root_dir)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(
        description="Clones config and creates Maven multi module project"
    )
    parser.add_argument(
        "-r",
        "--root_dir",
        default=".",
        help="The root dir of clones and multi module project",
    )
    parser.add_argument("-b", "--branch", default="develop", help="The branch to clone")
    p_args = parser.parse_args()

    clone_config_and_create_mmp(p_args.root_dir, p_args.branch)
