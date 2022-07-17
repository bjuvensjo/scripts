#!/usr/bin/env python3
import argparse
from os import walk
from sys import argv


def has_ending(endings, file_names):
    return any([e in endings for e in [n.split(".")[-1] for n in file_names]])


def is_included(snapshots, dir_path):
    return snapshots or not dir_path.upper().endswith("-SNAPSHOT")


def get_artifacts(repo_dir, endings=("pom", "jar"), snapshots=False):
    return sorted(
        [
            dir_path[len(repo_dir) + 1 :]
            for dir_path, dir_names, file_names in walk(repo_dir)
            if has_ending(endings, file_names) and is_included(snapshots, dir_path)
        ]
    )


def list_repo(repo_dir, endings=("pom", "jar"), snapshots=False):
    for artifact in get_artifacts(repo_dir, endings, snapshots):
        split = artifact.split("/")
        print(
            f"""<dependency>
    <groupId>{".".join(split[:-2])}</groupId>
    <artifactId>{split[-2]}</artifactId>
    <version>{split[-1]}</version>
</dependency>"""
        )


def parse_args(args):
    parser = argparse.ArgumentParser(description="List artifacts in repository")
    parser.add_argument(
        "repo_dir",
        help="Repository directory",
    )
    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    list_repo(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
