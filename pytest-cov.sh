#!/usr/bin/env bash
pytest --cov vang/artifactory --cov vang/azdo --cov vang/bitbucket --cov vang/core --cov vang/git --cov vang/github --cov vang/jenkins --cov vang/maven --cov vang/misc --cov vang/nexus3 --cov vang/pio --cov vang/tfs --cov vang/wildcat --cov-report html
