#!/usr/bin/env bash

# usage blob2db.sh [date to process] 2019/3/15

docker run -v /tmp:/tmp -t mmf /usr/bin/python3.7 /mmf/blob2db.py %1


