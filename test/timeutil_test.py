import unittest

from log.timeutil import *

class MyTestCase(unittest.TestCase):

    def test_timestamp(self):
        """
        def timestamp():
        now = datetime.datetime.utcnow()
        return int(now.timestamp())
        """
        print ("TIMESTAMP->", timestamp())

    def test_date_string(self):
        """
        def date_string():
        time = datetime.datetime.fromtimestamp(timestamp())

        return time.strftime('%Y-%m-%d')
        """
        print("DATE->", date_string())

    def test_time_stamp_string(self):
        """
        def time_stamp_string():
        time = datetime.datetime.fromtimestamp(timestamp())
        return time.isoformat()
        """
        print("TIMESTAMP->", time_stamp_string())

    def test_time_sec(self):
        """
        def time_sec(iso_time):
        sec = datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        return int(sec.timestamp())
        """
        print("TIMESEC->", time_sec("1970-01-01T00:00:01.00Z"))
        print("TIMESEC->", time_sec("1976-01-01T00:00:00.000Z"))


if __name__ == '__main__':
    unittest.main()


