#!/bin/bash

docker run --restart=always -v /tmp:/mexlog -t mmf /usr/bin/python3.7 /mmf/net2log.py /mexlog /mexlog/NET2LOG-FLG WORKA &
docker run --restart=always -v /tmp:/mexlog -t mmf /usr/bin/python3.7 /mmf/net2log.py /mexlog /mexlog/NET2LOG-FLG WORKB &





