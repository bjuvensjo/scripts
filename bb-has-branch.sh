#!/bin/bash

key=$1
repo=$2
branch=$3

branches="$(bb-get-branches "$key" "$repo" "$branch")"
if [ -n "$(grep "\"displayId\":\"$branch\"" <<< "$branches")" ] && [ -n "$(grep "\"size\":1" <<< "$branches")" ]; then
    echo "$branch"
fi
