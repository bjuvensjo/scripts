#!/usr/bin/env python3

import argparse
from sys import argv

from vang.jenkins.api import call


def do_trigger_builds(names):
    return [
        (
            name,
            call(
                f"/job/{name}/build",
                method="POST",
                only_response_code=True,
            ),
        )
        for name in names
    ]


def parse_args(args):
    parser = argparse.ArgumentParser(description="Trigger Jenkins jobs")
    parser.add_argument(
        "job_names",
        nargs="+",
        help="Jenkins job names",
    )
    return parser.parse_args(args)


def trigger_builds(job_names):
    for job_name, response_code in do_trigger_builds(job_names):
        print(job_name, response_code)


def main() -> None:  # pragma: no cover
    trigger_builds(**parse_args(argv[1:]).__dict__)


if __name__ == "__main__":  # pragma: no cover
    main()
