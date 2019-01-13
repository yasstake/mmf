import datetime

def timestamp():
    now = datetime.datetime.utcnow()
    return int(now.timestamp())


def date_string():
    time = datetime.datetime.fromtimestamp(timestamp())

    return time.strftime('%Y-%m-%d')

def time_stamp_string():
    time = datetime.datetime.fromtimestamp(timestamp())
    return time.isoformat()

def time_sec(iso_time):
    sec = datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    return int(sec.timestamp())
