#!/bin/bash

for key in "$@"
do
    limit=25
    start=0
    isLastPage="false"

    while [ "$isLastPage" = "false" ]
    do
        response=$(curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects/$key/repos\?limit\=$limit\&start=$start)
        split=( $(sed -E -e 's/ //g' -e 's/{"size":([0-9]+).*"isLastPage":([^,]+),"values":\[{(.*)/\1 \2 \3/p' <<< "$response") )
        
        size=${split[0]}
        isLastPage="${split[1]}"
        values="${split[2]}"

        if [ "$isLastPage" = "false" ]
        then
            split=( $(sed -E 's/(.*)"nextPageStart":([0-9]+).*/\1 \2/p' <<< "$values") )
            values="${split[0]}"
            start="${split[1]}"
        fi

        if [ $size != 0 ]
        then
            repos=( $(sed 's/}]}},{/ /g'<<< "$values") )
            for repo in "${repos[@]}"; do
                name=$(sed -E 's/"slug":"([^"]+).*/\1/' <<< "$repo")
                clone_dir="$key/$(sed 's/\./\//g' <<< $name)"
                clone_url=$(sed -E 's/.*"clone":\[{"href":"([^"]+).*/\1/' <<< "$repo")
                echo "git clone $clone_url $clone_dir"
            done
        fi
    done
done
