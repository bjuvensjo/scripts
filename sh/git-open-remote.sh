#!/usr/bin/env bash

if [ -z "$1" ]; then
    git_dir="./.git"
else
    git_dir="$1/.git"
fi

clone_url="$(git --git-dir="$git_dir" remote get-url origin | sed -E "s/(.*\/\/).*@(.*)/\1\2/" )"
commits_url="$(sed -E "s/(.*\/)scm(.*\/)(.*)\.git/\1projects\2repos\/\3\/commits/" <<< $clone_url)"
echo "clone_url: $clone_url"
echo "commits_url: $commits_url"
# open "$clone_url"
open "$commits_url"
