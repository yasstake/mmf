import unittest
import re

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
        self.assertEqual(time_sec("1970-01-01T00:00:01.00Z"), 1)

        print("TIMESEC->", time_sec("1970-01-01T00:00:01.00+00:00"))
        self.assertEqual(time_sec("1970-01-01T00:00:01.00+00:00"), 1)

        print("TIMESEC->", time_sec("1970-01-01T00:00:01.00+09:00"))
        self.assertEqual(time_sec("1970-01-01T00:00:01.00+09:00"), -32399)

        print("TIMESEC->", time_sec("2019-03-07T12:51:05.344823+00:00"))


    def test_timestamp2(self):
            t0 = time_stamp_string(0)
            print(t0)

            t1 = time_stamp_string(1)
            print(t1)

            t1000 = time_stamp_string(1000)
            print(t1000)



    def test_timestamp2_1(self):
        t0 = time_stamp_string(0.1)
        t1 = time_sec(t0)

        print(t1)


    def test_timestamp2_2(self):
        print(timestamp())
        print("TIMESEC->", time_sec("2019-03-03T10:49:01.00+09:00"))
        print("TIMESEC->", time_sec("2019-03-03T10:40:01.00+00:00"))

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


    def test_timestemp3_1(self):
        time1 = "2019-03-03T01:50:34.0Z"
        time2 = 1551577834
        tsec1 = time_sec(time1)

        self.assertEqual(tsec1, time2)



    def test_timestemp4(self):
        time1 = "2019-03-02T14:55:16.855Z"
        time2 = 1551506117
        print("TIME4->")
        print(time_stamp_string(time2))


    def test_timestemp4(self):
        print(timestamp())

    def test_timestamp5(self):
        t = time_stamp_string()
        print(t)

        unixtime = timestamp()
        unixtime2 = time_sec(t)

        self.assertEqual(int(unixtime/10), int(unixtime2/10))


    def test_logtime(self):
        time = time_sec('2019-03-07T22:09:58.00Z')
        time2 = 1551996598
        print(time, time2)
        self.assertEqual(time, time2)

        time2 = time_sec('2019-03-08T13:49:10.740+00:00')
        time2 = time_sec('2019-03-08T13:49:10.740Z')
        time2 = time_sec('2019-03-08T13:49:10.740')

        time2 = time_sec('2019-03-08T12:00:00.000+00:00')


    def test_reg(self):
        print(re.search("\+", '2019-03-08T13:49:10.740+00:00'))


    def test_time_path(self):
        print(date_path(2019, 3, 1, separator='/'))
        print(date_path(2019, 3, 1, -1))
        print(date_path(2019, 3, 1, -2))

    def test_midnight(self):
        start = 1552692811
        start_m=1552694400
        end_m  =1552867199
        end =   1552873616

        print(time_stamp_string(start))
        print(time_stamp_string(start_m))
        print(time_stamp_string(end_m))
        print(time_stamp_string(end))

        print(date_string(start_m))
        print(date_string(end_m))


    def test_time_sprit_day(self):
        print(sprit_timestamp(0))


    def test_time_date_time_path(self):
        time = time_stamp_object(0)
        print(time.year, time.month, time.day, time.hour, time.minute, time.second)

        self.assertEqual(time.year, 1970)
        self.assertEqual(time.month, 1)
        self.assertEqual(time.day, 1)
        self.assertEqual(time.hour, 0)
        self.assertEqual(time.minute, 0)
        self.assertEqual(time.second, 0)


#:[{"timestamp":"2019-02-28T23:02:14.807Z","side":"Buy","size":104,"price":3791.5,"tickDirection":"ZeroPlusTick"}],
#"TIME":1551362533}

if __name__ == '__main__':
    unittest.main()


