from argparse import ArgumentParser, BooleanOptionalAction
from os import environ


def get_parser(
    description: str, project: bool = True
) -> ArgumentParser:  # pragma: no cover
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-au",
        "--azure_devops_url",
        default="https://dev.azure.com",
        help="The Azure DevOps REST API base url",
    )
    parser.add_argument(
        "--verify_certificate",
        default=True,
        action=BooleanOptionalAction,
        help="If certificate of Azure should be verified",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=environ.get("AZDO_TOKEN", ""),
        help="The Azure DevOps authorisation token",
    )
    parser.add_argument(
        "-o",
        "--organisation",
        default=environ.get("AZDO_ORGANISATION", ""),
        help="The Azure DevOps organisation",
    )
    if project:
        parser.add_argument(
            "-p",
            "--project",
            default=environ.get("AZDO_PROJECT", ""),
            help="The Azure DevOps project",
        )
    return parser
