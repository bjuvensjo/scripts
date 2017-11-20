#!/bin/bash

key=$1
repo=$2
branch=$3

if [ -n "$(bb-get-branches "$key" "$repo" "$branch" | grep "\"displayId\":\"$branch\"")" ]; then
    echo "$branch"
fi
