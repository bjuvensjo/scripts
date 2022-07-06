#!/usr/bin/env python3

import argparse
from os import environ
from sys import argv

from vang.jenkins.api import call

FAILURE = "FAILURE"
SUCCESS = "SUCCESS"
NOT_BUILT = "NOT_BUILT"
UNKNOWN = "UNKNOWN"


def map_color(color):
    if color == "blue":
        return SUCCESS
    if color == "red":
        return FAILURE
    if color == "notbuilt":
        return NOT_BUILT
    return UNKNOWN


def get_jobs(
    statuses=(FAILURE, SUCCESS, NOT_BUILT, UNKNOWN),
    only_names=False,
    url=environ.get("JENKINS_REST_URL", None),
    username=environ.get("JENKINS_USERNAME", None),
    password=environ.get("JENKINS_PASSWORD", None),
    verify_certificate=not environ.get("JENKINS_IGNORE_CERTIFICATE", None),
    view=None,
):
    jobs = call(
        f"/view/{view}/api/json" if view else "/api/json",
        rest_url=url,
        username=username,
        password=password,
        verify_certificate=verify_certificate,
    )["jobs"]
    return [
        job["name"] if only_names else job
        for job in jobs
        if map_color(job.get("color", None)) in statuses
    ]


def parse_args(args):
    parser = argparse.ArgumentParser(description="Get Jenkins jobs")
    parser.add_argument(
        "-n", "--only_names", action="store_true", help="Get only job names"
    )
    parser.add_argument("-v", "--view", default=None, help="Get only jobs in view")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-f",
        "--only_failures",
        action="store_true",
        help="Only failure jobs",
    )
    group.add_argument(
        "-s",
        "--only_successes",
        action="store_true",
        help="Only success jobs",
    )
    group.add_argument(
        "-b",
        "--only_not_built",
        action="store_true",
        help="Only not built jobs",
    )
    group.add_argument(
        "-u",
        "--only_unknown",
        action="store_true",
        help="Only unknown status jobs",
    )
    return parser.parse_args(args)


def main(only_failures, only_successes, only_names, only_not_built, only_unknown, view):
    if only_failures:
        job_statuses = [FAILURE]
    elif only_successes:
        job_statuses = [SUCCESS]
    elif only_not_built:
        job_statuses = [NOT_BUILT]
    elif only_unknown:
        job_statuses = [UNKNOWN]
    else:
        job_statuses = [FAILURE, SUCCESS, NOT_BUILT, UNKNOWN]

    for a_job in get_jobs(job_statuses, only_names, view=view):
        print(a_job)


if __name__ == "__main__":  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
