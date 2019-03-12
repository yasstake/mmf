#!/bin/bash

/usr/bin/python3.7 /mmf/net2log.py /mexlog /mexlog/NET2LOG-FLG
gzip /mexlog/*.log

sleep 100


