#!/usr/bin/env bash

docker rm $(docker ps -q -a)

echo 'start daemon A'
docker run --name WORKER-A -d -v /tmp:/mexlog --restart=always -t mmf bash /net2log.sh WORKER-A

sleep 10

echo 'start daemon B'
docker run --name WORKER-B -d -v /tmp:/mexlog --restart=always -t mmf bash /net2log.sh WORKER-B





