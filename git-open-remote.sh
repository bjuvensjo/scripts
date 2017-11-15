#!/bin/bash

if [ -z "$1" ]; then
    git_dir="./.git"
else
    git_dir="$1/.git"
fi

clone_url="$(git --git-dir="$git_dir" remote get-url origin | sed -E "s/(.*\/\/).*@(.*)/\1\2/" )"
open "$clone_url"
