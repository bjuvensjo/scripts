#!/bin/bash

key=$1
repo=$2
branch=$3

has_branch="$(curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects/$key/repos/$repo/branches?filterText=$branch | grep "\"displayId\":\"$branch\"")"

if [ -n "$has_branch" ]; then
    echo "$branch"
fi
