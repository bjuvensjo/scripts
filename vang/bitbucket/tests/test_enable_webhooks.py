#!/usr/bin/env python3
from argparse import Namespace
from pytest import raises
from unittest.mock import call, patch

from vang.bitbucket.enable_webhooks import enable_repo_web_hook
from vang.bitbucket.enable_webhooks import enable_web_hook
from vang.bitbucket.enable_webhooks import main
from vang.bitbucket.enable_webhooks import parse_args


@patch('vang.bitbucket.enable_webhooks.call', return_value='enabled')
def test_enable_repo_web_hook(mock_enable_repo_web_hook):
    assert (('project', 'repo'), 'enabled') == enable_repo_web_hook(
        ('project', 'repo'), 'url')
    assert [
        call(
            '/rest/api/1.0/projects/project/repos/repo/settings/hooks/'
            'com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:'
            'postReceiveHook/enabled', '{"hook-url-0": "url"}', 'PUT')
    ] == mock_enable_repo_web_hook.mock_calls


@patch(
    'vang.bitbucket.enable_webhooks.enable_repo_web_hook',
    side_effect=lambda x, y: (x, 'enabled'))
def test_enable_web_hook(mock_enable_repo_web_hook):
    assert [
        (('projects', 'repo1'), 'enabled'),
        (('project', 'repo2'), 'enabled'),
    ] == enable_web_hook(
        [
            ('projects', 'repo1'),
            ('project', 'repo2'),
        ],
        'url',
        max_processes=5,
    )
    assert [
        call(('projects', 'repo1'), 'url'),
        call(('project', 'repo2'), 'url')
    ] == mock_enable_repo_web_hook.mock_calls


@patch('builtins.print')
@patch(
    'vang.bitbucket.enable_webhooks.enable_web_hook',
    side_effect=[[
        [('project', 'repo1'), {
            'enabled': True
        }],
        [('project', 'repo1'), {
            'enabled': True
        }],
    ]])
@patch(
    'vang.bitbucket.enable_webhooks.get_repo_specs',
    return_value=[
        ('project', 'repo1'),
        ('project', 'repo2'),
    ])
def test_main(mock_get_repo_specs, mock_enable_web_hook, mock_print):
    assert not main('url', dirs=None, projects=['project'])
    assert [call(None, None, ['project'])] == mock_get_repo_specs.mock_calls
    assert [call([
        ('project', 'repo1'),
        ('project', 'repo2'),
    ], 'url')] == mock_enable_web_hook.mock_calls
    assert [
        call('project/repo1: enabled'),
        call('project/repo1: enabled'),
    ] == mock_print.mock_calls


def test_parse_args():
    with raises(SystemExit):
        parse_args([])

    assert Namespace(
        dirs=['dir1', 'dir2'],
        projects=None,
        repos=None,
        url='url',
    ) == parse_args(['url', '-d', 'dir1', 'dir2'])

    assert Namespace(
        dirs=['.'],
        projects=['project1', 'project2'],
        repos=None,
        url='url',
    ) == parse_args(['url', '-p', 'project1', 'project2'])

    assert Namespace(
        dirs=['.'],
        projects=None,
        repos=['repo1', 'repo2'],
        url='url',
    ) == parse_args(['url', '-r', 'repo1', 'repo2'])
