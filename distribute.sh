#!/usr/bin/env bash

# Remove old
rm -rf dist

# Make sure you have the latest version of PyPA’s build installed
python3 -m pip install --upgrade build

# Create source (tar.gz) and built (whl) distributions in dist
python3 -m build

# Install Twine
python3 -m pip install --upgrade twine

# Run Twine to upload all of the archives under dist
python3 -m twine upload dist/*
