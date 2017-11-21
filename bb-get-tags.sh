#!/bin/bash

key=$1
repo=$2
tag=$3

curl -s -u $U:$P http://cuso.edb.se/stash/rest/api/1.0/projects/$key/repos/$repo/tags?filterText=$tag
