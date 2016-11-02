#!/bin/bash

if [ $# -lt "1" ]
then
    echo "Usage ./jb.sh <names>, e.g. ./jb.sh EVPS_config.v1_0_develop EVAP_app.common.businessproxy.rest.v1_0_develop"
fi

read -p "jenkins username: " username
read -s -p "jenkins password: " password
echo ""

for job in $@
do
    echo "********************************************************************************"
    echo "$job"
    curl -i --user $username:$password -X POST http://10.46.64.51:8080/job/$job/build
    Echo "********************************************************************************"
done
