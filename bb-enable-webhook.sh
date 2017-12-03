#!/bin/bash

git_dir="$(pwd)/.git"
clone_url="$(git --git-dir $git_dir remote get-url origin | sed -E "s/(.*\/\/).*@(.*)/\1\2/" )"

project="$(sed -E "s/.*\/(.*)\/.*/\1/" <<< $clone_url | tr '[:lower:]' '[:upper:]')"
repo="$(sed -E "s/.*\/(.*)\.git/\1/" <<< $clone_url)"

api_url="http://cuso.edb.se/stash/rest/api/1.0/projects/$project/repos/$repo/settings/hooks/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin:postReceiveHook/enabled"

data="{\"hook-url-0\":\"http://10.46.64.31:8000/cgi-bin/webhook/\"}"

curl -s -N -u $U:$P -H "Content-Type: application/json" -X PUT -d "$data" "$api_url"
