#!/usr/bin/env bash

sudo docker rm $(docker ps -f status=exited -f status=created -f status=dead -f status=paused -q)

echo 'start'
sudo docker run --name $1$2$3 -v /tmp:/bitlog -t blob2export python3.7 /mmf/blob2export.py $1 $2 $3

