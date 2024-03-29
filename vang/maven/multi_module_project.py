#!/usr/bin/env python3
""" Makes Maven multi module project. """

from argparse import ArgumentParser
from os import getcwd, makedirs
from os.path import dirname, normpath, realpath, relpath, sep
from sys import argv

import vang.maven.pom as pom

POM_TEMPLATE = """<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>###group_id###</groupId>
    <artifactId>###artifact_id###</artifactId>
    <version>###version###</version>
    <packaging>pom</packaging>
    <modules>
###modules###
    </modules>
</project>"""


def get_pom(pom_infos, output_dir, group_id, artifact_id, version):
    """Returns multi module pom content for pom_infos
    with paths relative to output_dir."""
    modules = "\n".join(
        "        <module>{}</module>".format(
            relpath(realpath(dirname(info["pom_path"])), realpath(output_dir)).replace(
                "\\", "/"
            )
        )
        for info in sorted(pom_infos, key=lambda d: d["pom_path"])
    )
    return (
        POM_TEMPLATE.replace("###group_id###", group_id)
        .replace("###artifact_id###", artifact_id)
        .replace("###version###", version)
        .replace("###modules###", modules)
    )


def make_project(pom_infos, output_dir, group_id, artifact_id, version):
    """Makes a Maven multi module project."""
    pom = get_pom(pom_infos, output_dir, group_id, artifact_id, version)
    makedirs(output_dir)
    with open(
        normpath(f"{output_dir}/pom.xml"),
        "wt",
        encoding="utf-8",
    ) as pom_file:
        pom_file.write(pom)


def get_pom_infos(source_dir):
    pom_infos = []
    for pom_path in pom.get_pom_paths(source_dir):
        try:
            pom_info = pom.get_pom_info(pom_path)
            pom_infos.append(pom_info)
        except Exception as e:  # pragma: no cover
            print(f"Can not add {pom_path}")
            print(e)
    return pom_infos


def parse_args(args):
    parser = ArgumentParser(description="Create Maven multi module project")
    parser.add_argument(
        "-d", "--use_defaults", action="store_true", help="Create with default values."
    )
    return parser.parse_args(args)


def multi_module_project(use_defaults):
    artifact_id = f"ws-{getcwd().split(sep)[-1]}"
    defaults = {
        "group_id": "my.group",
        "artifact_id": artifact_id,
        "version": "1.0.0-SNAPSHOT",
        "source_dir": ".",
        "output_dir": artifact_id,
    }

    if use_defaults:
        pom_infos = get_pom_infos(defaults["source_dir"])
        make_project(pom_infos, **defaults)
    else:

        group_id = str(
            input(f'groupId (default {defaults["group_id"]}): ') or defaults["group_id"]
        )
        artifact_id = str(
            input(f'artifactId (default {defaults["artifact_id"]}): ')
            or defaults["artifact_id"]
        )
        version = str(
            input(f'version (default {defaults["version"]}): ') or defaults["version"]
        )
        source_dir = normpath(
            str(
                input(f'sourceDir: (default {defaults["source_dir"]})')
                or defaults["source_dir"]
            )
        )
        output_dir = normpath(
            str(
                input(f'outputDir: (default {defaults["output_dir"]})')
                or defaults["output_dir"]
            )
        )

        pom_infos = get_pom_infos(source_dir)
        make_project(pom_infos, output_dir, group_id, artifact_id, version)


def main() -> None:  # pragma: no cover
    multi_module_project(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
