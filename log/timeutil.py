import datetime
import re


#from pytz import utc



def time_sec(iso_time):
    if iso_time.endswith('Z'):
        iso_time = iso_time.replace('Z', '+0000')
    elif not re.search('\+', iso_time):
        iso_time = iso_time + '+0000'

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


def date_string(time = None, separator='-'):
    if not time:
        time = timestamp()
    time = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)

    return time.strftime('%Y'+ separator + '%m' + separator +'%d')


def time_stamp_object(time = None):
    if time is None:
        time = timestamp()

    return datetime.datetime.utcfromtimestamp(time)


def time_stamp_string(time = None):
    time = time_stamp_object(time)

    return time.isoformat() + 'Z'


def date_path(yyyy, mm, dd, offset=0, separator='-'):
    date = datetime.date(yyyy, mm, dd) + datetime.timedelta(days=offset)

    return '{:04d}'.format(date.year) + separator + '{:02d}'.format(date.month) + separator + '{:02d}'.format(date.day)


def sprit_timestamp(time):
    time = time_stamp_object(time)

    return time.year, time.month, time.day, time.hour, time.minute
