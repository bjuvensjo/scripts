#!/usr/bin/env python3
import argparse
import re
from os import environ
from sys import argv

from requests import get, post


# Found no API for listing views so scraping the web page...
def list_views(url, username, password, verify_certificate):
    response = get(url=url, auth=(username, password), verify=verify_certificate)
    return {r for r in re.findall(r'href="/view/([^/]+)/', response.text, re.MULTILINE)}


def get_view_xml(name, job_names=tuple()):
    job_names_xml = "".join([f"<string>{n}</string>" for n in job_names])
    return f"""<hudson.model.ListView>
        <name>{name}</name>
        <filterExecutors>false</filterExecutors>
        <filterQueue>false</filterQueue>
        <properties class="hudson.model.View$PropertyList"/>
        <jobNames>{job_names_xml}</jobNames>
        <jobFilters/>
        <columns>
            <hudson.views.StatusColumn/>
            <hudson.views.WeatherColumn/>
            <hudson.views.JobColumn/>
            <hudson.views.LastSuccessColumn/>
            <hudson.views.LastFailureColumn/>
            <hudson.views.LastDurationColumn/>
            <hudson.views.BuildButtonColumn/>
        </columns>
        <recurse>false</recurse>
    </hudson.model.ListView>"""


def get_view(name, url, username, password, verify_certificate):
    uri = f"/view/{name}/config.xml"
    return get(url=f"{url}{uri}", auth=(username, password), verify=verify_certificate)


def view_exists(name, url, username, password, verify_certificate):
    return (
        get_view(name, url, username, password, verify_certificate).status_code == 200
    )


def do_post(uri, url, username, password, verify_certificate, data=None):
    return post(
        url=f"{url}{uri}",
        data=data if data else None,
        headers={"Content-Type": "text/xml"},
        auth=(username, password),
        verify=verify_certificate,
    )


def create_view(name, job_names, url, username, password, verify_certificate):
    uri = f"/createView?name={name}"
    return do_post(
        uri, url, username, password, verify_certificate, get_view_xml(name, job_names)
    ).status_code


def delete_view(name, url, username, password, verify_certificate):
    uri = f"/view/{name}/doDelete"
    return do_post(uri, url, username, password, verify_certificate).status_code


def update_view(name, job_names, url, username, password, verify_certificate):
    uri = f"/view/{name}/config.xml"
    return do_post(
        uri, url, username, password, verify_certificate, get_view_xml(name, job_names)
    ).status_code


def set_view(name, job_names, url, username, password, verify_certificate):
    params = (url, username, password, verify_certificate)
    if view_exists(name, *params):
        return update_view(name, job_names, *params)
    return create_view(name, job_names, *params)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Set (Create/Update Jenkins view with jobs"
    )
    parser.add_argument(
        "name",
        help="Jenkins view name",
    )
    parser.add_argument(
        "job_names",
        nargs="+",
        help="Jenkins job names",
    )
    parser.add_argument(
        "--url", "-u", help="Jenkins url", default=environ.get("JENKINS_REST_URL", None)
    )
    parser.add_argument(
        "--username",
        "-n",
        help="Jenkins username",
        default=environ.get("JENKINS_USERNAME", None),
    ),
    parser.add_argument(
        "--password",
        "-p",
        help="Jenkins password",
        default=environ.get("JENKINS_PASSWORD", None),
    )
    parser.add_argument(
        "--verify_certificate",
        "-v",
        help="Verify Jenkins certificate",
        default=not environ.get("JENKINS_IGNORE_CERTIFICATE", None),
    )
    return parser.parse_args(args)


if __name__ == "__main__":  # pragma: no cover
    response_code = set_view(**parse_args(argv[1:]).__dict__)
    print(response_code)
