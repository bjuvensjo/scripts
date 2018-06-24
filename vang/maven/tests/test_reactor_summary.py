#!/usr/bin/env python3

from os.path import dirname

from vang.maven.reactor_summary import get_reactor_summary

def test_reactor_summary():
    with open(dirname(__file__) + '/mvn.log', 'rt', encoding='utf-8') as f:
        mvn_log = f.readlines()
        assert ['[INFO] myorg:app.admin 0.0.1-SNAPSHOT ................. SUCCESS [ 11.095 s]',
                '[INFO] config-apache-proxy 1.0.0-SNAPSHOT ................. SUCCESS [  4.300 s]'] == get_reactor_summary(mvn_log)