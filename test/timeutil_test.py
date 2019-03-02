import unittest

from log.timeutil import *

class MyTestCase(unittest.TestCase):

    def test_timestamp(self):
        """
        def timestamp():
        now = datetime.datetime.utcnow()
        return int(now.timestamp())
        """
        print ("TIMESTAMP1->", timestamp())
        print("TIMESTAMP2->", time_stamp_string())


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
        print("TIMESEC->", time_sec("2019-03-01T01:00:00.000Z"))

    def test_timestamp2(self):
        print('TIME->', time_stamp_string(1551362541))
        print('tran time->', time_stamp_string(1551362533))

    def test_timestamp3(self):
        print("TIME3->", time_stamp_string(1551362584))
        print("time3->", time_sec("2019-02-28T23:03:04.818Z"))
        sec_string = "2019-02-28T23:03:04.818Z"
        tsec = time_sec(sec_string)
        sec_string2 = time_stamp_string(tsec)
        tsec2 = time_sec(sec_string2)
        print(tsec, "/", tsec2)
        print(sec_string, '/', sec_string2)
        self.assertEqual(tsec, tsec2)

        #       {"table": "trade", "action": "insert", "data": [
        #    {"timestamp": "2019-02-28T23:03:04.818Z", "side": "Buy", "size": 4000, "price": 3794,
        #     "tickDirection": "ZeroPlusTick"}], "TIME": 1551362584}






#:[{"timestamp":"2019-02-28T23:02:14.807Z","side":"Buy","size":104,"price":3791.5,"tickDirection":"ZeroPlusTick"}],
#"TIME":1551362533}

if __name__ == '__main__':
    unittest.main()


