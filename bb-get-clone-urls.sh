#!/bin/bash

for key in "$@"
do
    response=$(curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects/$key/repos\?limit\=9999)
    split=( $(sed -E -e 's/ //g' -e 's/{"size":([0-9]+).*"values":\[{(.*)/\1 \2/p' <<< "$response") )
    if [ ${split[0]} != 0 ]
    then
        repos=( $(sed 's/}]}},{/ /g'<<< "${split[1]}") )
        for repo in "${repos[@]}"; do
            name=$(sed -E 's/"slug":"([^"]+).*/\1/' <<< "$repo")
            clone_dir="$key/$(sed 's/\./\//g' <<< $name)"
            clone_url=$(sed -E 's/.*"clone":\[{"href":"([^"]+).*/\1/' <<< "$repo")
            echo "git clone $clone_url $clone_dir"
        done
    fi
done
