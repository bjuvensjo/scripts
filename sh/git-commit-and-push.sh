#!/usr/bin/env bash

if [ -z "$1" ]; then
    git_dir="./.git"
else
    git_dir="$1/.git"
fi

git --git-dir="$git_dir" add --all
git --git-dir="$git_dir" commit -m "Misc updates"
git --git-dir="$git_dir" push
