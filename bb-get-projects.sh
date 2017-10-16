#!/bin/bash

curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects\?limit\=9999 \
    | tr '{' '\n' \
    | grep key \
    | sed -E 's/.*"key":"([^"]+).*"name":"([^"]+).*/\1:\2/'
