#!/bin/bash

# grep on projects
bb-get-clone-urls $(bb-get-projects \
                        | grep "$1" \
                        | sed 's/:.*//' \
                        | xargs)
