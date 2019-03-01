import datetime

def timestamp():
    now = datetime.datetime.utcnow()
    return int(now.timestamp())


def date_string(time = timestamp()):
    time = datetime.datetime.fromtimestamp(time)

    return time.strftime('%Y-%m-%d')

def time_stamp_string(time = timestamp()):
    time = datetime.datetime.utcfromtimestamp(time)
    time = time.replace(tzinfo=datetime.timezone.utc)
    return time.isoformat()

def time_sec(iso_time):
    sec = datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    print("sec->", sec)
    sec = sec.replace(tzinfo=datetime.timezone.utc)
    print("sec2->", sec)

    return sec.timestamp()
