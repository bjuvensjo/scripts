#!/usr/bin/env python3

import argparse
from os import environ
from sys import argv

from vang.jenkins.api import call


def delete_jobs(
    names,
    url=environ.get("JENKINS_REST_URL", None),
    username=environ.get("JENKINS_USERNAME", None),
    password=environ.get("JENKINS_PASSWORD", None),
    verify_certificate=not environ.get("JENKINS_IGNORE_CERTIFICATE", None),
):
    return [
        (
            job_name,
            call(
                f"/job/{job_name}/doDelete",
                method="POST",
                only_response_code=True,
                rest_url=url,
                username=username,
                password=password,
                verify_certificate=verify_certificate,
            ),
        )
        for job_name in names
    ]


def parse_args(args):
    parser = argparse.ArgumentParser(description="Delete Jenkins jobs")
    parser.add_argument(
        "job_names",
        nargs="+",
        help="Jenkins job names",
    )
    return parser.parse_args(args)


def main(job_names):
    for a_job_name, a_response_code in delete_jobs(job_names):
        print(a_job_name, a_response_code)


if __name__ == "__main__":  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
