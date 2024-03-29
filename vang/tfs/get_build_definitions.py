#!/usr/bin/env python3

import argparse
from json import dumps
from sys import argv

from vang.tfs.api import call_url
from vang.tfs.list_build_definitions import do_list_build_definitions


def do_get_build_definitions(
    organisations=None,
    projects=None,
    filter_name=None,
):
    build_definitions_dict = do_list_build_definitions(
        organisations, projects, filter_name
    )
    return {
        name: call_url(definition["url"])
        for name, definition in build_definitions_dict.items()
    }


def get_build_definitions(
    organisations, projects, filter_name=None, format_output=False
):
    for name, definition in do_get_build_definitions(
        organisations, projects, filter_name
    ).items():
        json = dumps(definition, indent=4) if format_output else dumps(definition)
        print(json)


def parse_args(args):
    parser = argparse.ArgumentParser(description="Get TFS build definitions")
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument(
        "-o", "--organisations", nargs="+", help="TFS organisations, e.g organisation"
    )
    required_group.add_argument(
        "-p", "--projects", nargs="+", help="TFS projects, e.g organisation/project"
    )

    parser.add_argument(
        "-fn",
        "--filter_name",
        help="Filters to definitions whose names equal this value. Append a * to filter to definitions whose names "
        "start with this value",
    )

    optional_group = parser.add_mutually_exclusive_group(required=False)
    optional_group.add_argument(
        "-f", "--format_output", action="store_true", help="Format output"
    )
    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    get_build_definitions(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
