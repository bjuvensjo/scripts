#!/usr/bin/env python3

import argparse
from collections import namedtuple
from os import environ
from pprint import pprint
from sys import argv

from requests import post

QueryArgs = namedtuple(
    "QueryArgs", "endpoint token query variables operation_name", defaults=({}, None)
)


def query_github(args: QueryArgs):
    json = {"query": args.query}
    if args.variables:
        json = json | {"variables": args.variables}
    if args.operation_name:
        json = json | {"operationName": args.operation_name}
    request = {
        "url": args.endpoint,
        "headers": {"Authorization": f"Bearer {args.token}"},
        "json": json,
    }
    r = post(**request)
    r.raise_for_status()
    return r.json()


def get_login(endpoint, token):
    query = "query { viewer { login }}"
    return query_github(QueryArgs(endpoint, token, query))["data"]["viewer"]["login"]


def get_repositories(endpoint, token, login, first=100, with_message=True):
    query = """query Repos($login: String!, $first: Int!, $withMessage: Boolean!) {
      repositoryOwner(login: $login) {
        repositories(first: $first) {
          nodes {
            name
            branches: refs(refPrefix: "refs/heads/", first: 100) {
              ...refFields
            }
            tags: refs(refPrefix: "refs/tags/", first: 100) {
              ...refFields
            }
          }
        }
      }
    }
    fragment refFields on RefConnection {
      nodes {
        name
        target {
          oid
          ... on Commit {
            message @include(if: $withMessage)
          }
        }
      }
    }"""
    variables = {"login": login, "first": first, "withMessage": with_message}
    response = query_github(
        QueryArgs(
            endpoint,
            token,
            query,
            variables,
        )
    )
    nodes = response["data"]["repositoryOwner"]["repositories"]["nodes"]

    def get_refs(refs):
        result = []
        for n in refs["nodes"]:
            r = {"name": n["name"], "commit": n["target"]["oid"]} | (
                {"message": n["target"]["message"]} if "message" in n["target"] else {}
            )
            result.append(r)
        return result

    return [
        {
            "name": r["name"],
            "branches": get_refs(r["branches"]),
            "tags": get_refs(r["tags"]),
        }
        for r in nodes
    ]


def parse_args(args):  # pragma: no cover
    parser = argparse.ArgumentParser(description="Query github")
    parser.add_argument(
        "--endpoint",
        "-e",
        default="https://api.github.com/graphql",
        help="The Github GraphQL endpoint",
    )
    parser.add_argument(
        "--token",
        "-t",
        default=environ.get("GITHUB_TOKEN", ""),
        help="The Github authorisation token",
    )
    parser.add_argument(
        "--login",
        "-l",
        default=None,
        help="The Github login",
    )
    parser.add_argument(
        "--first",
        "-f",
        default=100,
        help="The number of Github repos",
    )
    parser.add_argument(
        "--with_message",
        "-w",
        default=True,
        help="Include commit messages",
    )
    return parser.parse_args(args)


def main(
    endpoint: str, token: str, login: str, first: int, with_message: bool
) -> None:  # pragma: no cover
    login = login or get_login(endpoint, token)
    repositories = get_repositories(endpoint, token, login, first, with_message)
    for r in repositories:
        pprint(r)


if __name__ == "__main__":  # pragma: no cover
    main(**parse_args(argv[1:]).__dict__)
