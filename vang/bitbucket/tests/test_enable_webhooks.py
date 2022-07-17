from unittest.mock import call, patch

import pytest
from pytest import raises

from vang.bitbucket.enable_webhooks import enable_repo_web_hook
from vang.bitbucket.enable_webhooks import enable_web_hook
from vang.bitbucket.enable_webhooks import enable_web_hooks
from vang.bitbucket.enable_webhooks import parse_args


@patch("vang.bitbucket.enable_webhooks.call", return_value="enabled")
def test_enable_repo_web_hook(mock_enable_repo_web_hook):
    assert enable_repo_web_hook(("project", "repo"), "url") == (
        ("project", "repo"),
        "enabled",
    )
    assert mock_enable_repo_web_hook.mock_calls == [
        call(
            "/rest/api/1.0/projects/project/repos/repo/settings/hooks/"
            "com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:"
            "postReceiveHook/enabled",
            {"hook-url-0": "url"},
            "PUT",
        )
    ]


@patch(
    "vang.bitbucket.enable_webhooks.enable_repo_web_hook",
    side_effect=lambda x, y: (x, "enabled"),
)
def test_enable_web_hook(mock_enable_repo_web_hook):
    assert enable_web_hook(
        [
            ("projects", "repo1"),
            ("project", "repo2"),
        ],
        "url",
        max_processes=5,
    ) == [
        (("projects", "repo1"), "enabled"),
        (("project", "repo2"), "enabled"),
    ]
    assert mock_enable_repo_web_hook.mock_calls == [
        call(("projects", "repo1"), "url"),
        call(("project", "repo2"), "url"),
    ]


@patch("builtins.print")
@patch(
    "vang.bitbucket.enable_webhooks.enable_web_hook",
    side_effect=[
        [
            [("project", "repo1"), {"enabled": True}],
            [("project", "repo1"), {"enabled": True}],
        ]
    ],
)
@patch(
    "vang.bitbucket.enable_webhooks.get_repo_specs",
    return_value=[
        ("project", "repo1"),
        ("project", "repo2"),
    ],
)
def test_enable_webhooks(mock_get_repo_specs, mock_enable_web_hook, mock_print):
    assert not enable_web_hooks("url", dirs=None, projects=["project"])
    assert mock_get_repo_specs.mock_calls == [call(None, None, ["project"])]
    assert mock_enable_web_hook.mock_calls == [
        call(
            [
                ("project", "repo1"),
                ("project", "repo2"),
            ],
            "url",
        )
    ]
    assert mock_print.mock_calls == [
        call("project/repo1: enabled"),
        call("project/repo1: enabled"),
    ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "url foo",
        "url -d d -r r",
        "url -d d -p p",
        "url -r r -p p",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "url",
            {"dirs": ["."], "projects": None, "repos": None, "url": "url"},
        ],
        [
            "url -d d1 d2",
            {"dirs": ["d1", "d2"], "projects": None, "repos": None, "url": "url"},
        ],
        [
            "url -r r1 r2",
            {"dirs": ["."], "projects": None, "repos": ["r1", "r2"], "url": "url"},
        ],
        [
            "url -p p1 p2",
            {"dirs": ["."], "projects": ["p1", "p2"], "repos": None, "url": "url"},
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
