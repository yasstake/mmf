import re
import datetime
#from pytz import utc

def time_sec(iso_time):
    if re.match('\d$', iso_time):
        iso_time = iso_time + '+00:00'
    elif iso_time.endswith('Z'):
        iso_time = iso_time.replace('Z', '+00:00')

    sec = datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f%z")

    return sec.timestamp()


def timestamp():
    return _timestamp()

#    now = datetime.datetime.utcnow()
#    now.astimezone(utc)
#    return time_sec(now.isoformat() + "+00:00")

def _timestamp():
    now = datetime.datetime.now()
    return now.timestamp()


def date_string(time = None):
    if not time:
        time = timestamp()
    time = datetime.datetime.fromtimestamp(time)

    return time.strftime('%Y-%m-%d')

def time_stamp_string(time = None):
    if not time:
        time = timestamp()
    time = datetime.datetime.utcfromtimestamp(time)

    return time.isoformat() + 'Z'
