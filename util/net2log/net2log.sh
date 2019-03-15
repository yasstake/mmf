#!/bin/bash

worker_name = $1

/usr/bin/python3.7 /mmf/net2log.py /mexlog /mexlog/NET2LOG-FLG ${worker_name}
result = $?

/usr/bin/python3.7 /mmf/upload /mexlog

if  [${result} == 0]; then
    echo "sleep 1H"
    sleep 1h
fi


