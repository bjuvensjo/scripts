#!/usr/bin/env bash

if [ -z "$2" ]; then
    root="$(pwd)"
else
    root="$2"
fi

find "$root" -name ".git" -type d | while read git_dir; do
    cd "$git_dir/.."
    eval "$1"
done
