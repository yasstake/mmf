import unittest
from log.logdb import LogDb
from log.dbloader import DbLoader

import test.data as data
import json


class LogDbTest(unittest.TestCase):

    def test_create(self):
        log_db = LogDb()

        log_db.connect()
        log_db.create()

    def test_load(self):
        log_db = LogDb()
        log_db.connect()
        log_db.create()

        order_book = json.loads(data.order_book_depth)
        log_db.insert_order_book(100, order_book)
        log_db.insert_order_book(100, order_book)

    def test_message_to_list(self):
        log_db = LogDb()

        message = json.loads(data.order_book_depth_05)
        list = log_db.message_to_list(message)
        print(list)

    @staticmethod
    def connect():
        partial_message = """
        {
              "table":"orderBookL2",
              "keys":["symbol","id","side"],
              "types":{"id":"long","price":"float","side":"symbol","size":"long","symbol":"symbol"},
              "foreignKeys":{"side":"side","symbol":"instrument"},
              "attributes":{"id":"sorted","symbol":"grouped"},
              "action":"partial",
              "TIME": 1000,
              "data":[
                {"symbol":"XBTUSD","id":17999992000,"side":"Sell","size":100,"price":1000},
                {"symbol":"XBTUSD","id":17999993000,"side":"Sell","size":20,"price":70},
                {"symbol":"XBTUSD","id":17999994000,"side":"Sell","size":10,"price":51},
                {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":10,"price":50},
                {"symbol":"XBTUSD","id":17999996000,"side":"Buy","size":20,"price":40},
                {"symbol":"XBTUSD","id":17999997000,"side":"Buy","size":100,"price":30}
              ]
        }
        """
        update_message = """
        {
        "table":"orderBookL2",
        "action":"update",
        "TIME": 1001,
        "data":[
                {"symbol":"XBTUSD","id":17999992000,"side":"Sell","size":100,"price":100.5},
                {"symbol":"XBTUSD","id":17999993000,"side":"Sell","size":20,"price":100},
                {"symbol":"XBTUSD","id":17999994000,"side":"Sell","size":10,"price":99.5},
                {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":10,"price":99},
                {"symbol":"XBTUSD","id":17999996000,"side":"Buy","size":20,"price":98.5},
                {"symbol":"XBTUSD","id":17999997000,"side":"Buy","size":100,"price":98}
            ]
        }
        """

        db_loader = DbLoader()

        db_loader.open_db(':memory:')
        db_loader.load_line(partial_message)
        db_loader.load_line(update_message)

        return db_loader.get_db()


    def test_message_to_list_zip(self):
        log_db = LogDb()

        message = [1000,2,3,400]

        m2 = log_db.list_to_zip_string(message)

        m3 = log_db.zip_string_to_list(m2)
        print (m2)
        print ('\n')
        print (m3)
        assert(message == m3)

    @staticmethod
    def test_select_center_price():
        db = LogDbTest.connect()

        time_org = 1000

        time, center_price = db.select_center_price(time_org)

        assert(time == time_org)
        print(center_price)
        assert(center_price == 50.5)

        time, center_price = db.select_center_price(1001)
        print(center_price)
        assert(center_price == 99.5)


    @staticmethod
    def test_select_order_book():
        db = LogDbTest.connect()

    pass

    @staticmethod
    def test_select_sell_trade():
        db = LogDbTest.connect()
        pass

    @staticmethod
    def test_select_buy_trade():
        """
        :param time:
        :return: buy_trade list
        """
        db = LogDbTest.connect()
        pass

    @staticmethod
    def test_select_funding():
        """
        :param time:
        :return: time_to_remain, funding_rate
        """
        db = LogDbTest.connect()
        pass




if __name__ == '__main__':
    unittest.main()
