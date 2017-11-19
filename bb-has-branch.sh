#!/bin/bash

key=$1
repo=$2
branch=$3

if [ -n "$(curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects/$key/repos/$repo/branches?filterText=$branch | \
   grep "\"displayId\":\"$branch\"")" ]; then
    echo "$branch"
fi
