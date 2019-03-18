#!/usr/bin/env bash

# usage blob2db.sh [date to process e.g. 2019/3/15] [dbname default /tmp/bitlog.db]

docker run -v /tmp:/tmp -t mmf /usr/bin/python3.7 /mmf/blob2db.py %1 %2


