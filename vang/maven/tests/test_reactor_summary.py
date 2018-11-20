#!/usr/bin/env python3

from os.path import dirname

from vang.maven.reactor_summary import get_failures
from vang.maven.reactor_summary import get_project
from vang.maven.reactor_summary import get_reactor_summary
from vang.maven.reactor_summary import get_successes

import pytest


def test_get_reactor_summary():
    with open(dirname(__file__) + '/mvn.log', 'rt', encoding='utf-8') as f:
        mvn_log = f.readlines()
        assert [
            '[INFO] myorg:app.admin 0.0.1-SNAPSHOT ................. SUCCESS [ 11.095 s]',
            '[INFO] config-apache-proxy 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]'
        ] == get_reactor_summary(mvn_log)


@pytest.mark.parametrize("line, expected", [
    ('[INFO] myorg:app.admin 0.0.1-SNAPSHOT ................. SUCCESS [ 11.095 s]',
     'myorg:app.admin'),
    ('[INFO] config-apache-proxy 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]',
     'config-apache-proxy')
])
def test_get_project(line, expected):
    assert expected == get_project(line)


@pytest.mark.parametrize("reactor_summary, expected", [
    ([
        '[INFO] myorg:app.admin 0.0.1-SNAPSHOT ................. SUCCESS [ 11.095 s]',
        '[INFO] yourorg:app.admin 0.0.1-SNAPSHOT ................. FAILURE [ 11.095 s]',
        '[INFO] config-apache-proxy 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]',
        '[INFO] foofig-apache-proxy 1.0.0-SNAPSHOT ................. SKIPPED [  4.300 s]',
    ], ['myorg:app.admin', 'config-apache-proxy']),
])
def test_get_successes(reactor_summary, expected):
    assert expected == get_successes(reactor_summary)


@pytest.mark.parametrize("reactor_summary, expected", [
    ([
        '[INFO] myorg:app.admin 0.0.1-SNAPSHOT ................. SUCCESS [ 11.095 s]',
        '[INFO] yourorg:app.admin 0.0.1-SNAPSHOT ................. FAILURE [ 11.095 s]',
        '[INFO] config-apache-proxy 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]',
        '[INFO] foofig-apache-proxy 1.0.0-SNAPSHOT ................. SKIPPED [  4.300 s]',
    ], ['yourorg:app.admin', 'foofig-apache-proxy']),
])
def test_get_failures(reactor_summary, expected):
    assert expected == get_failures(reactor_summary)
