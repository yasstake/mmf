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
                {"symbol":"XBTUSD","id":17999994000,"side":"Sell","size":10,"price":60},
                {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":10,"price":50},
                {"symbol":"XBTUSD","id":17999996000,"side":"Buy","size":20,"price":40},
                {"symbol":"XBTUSD","id":17999997000,"side":"Buy","size":100,"price":30}
              ]
        }
        """

        db_loader = DbLoader()

        db_loader.open_db(':memory:')
        db_loader.load_line(partial_message)

        db = db_loader.get_db()
        print(db.select_center_price(1000))








if __name__ == '__main__':
    unittest.main()
