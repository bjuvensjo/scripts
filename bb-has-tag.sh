#!/bin/bash

key=$1
repo=$2
tag=$3

tags="$(bb-get-tags "$key" "$repo" "$tag")"
if [ -n "$(grep "\"displayId\":\"$tag\"" <<< "$tags")" ] && [ -n "$(grep "\"size\":1" <<< "$tags")" ]; then
    echo "$tag"
fi
