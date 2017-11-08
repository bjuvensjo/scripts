#!/bin/bash

if [ -z "$2" ]; then
    root="."
else
    root="$2"
fi

find "$root" -name ".git" -type d | while read git_dir; do
  cd "$git_dir/.."
  ($1)
done
