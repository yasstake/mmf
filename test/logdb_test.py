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
        log_db.insert_order_book_message(100, order_book)
        log_db.insert_order_book_message(100, order_book)

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

        sell_trade_data = """
        {"table":"trade","action":"insert","data":[{"timestamp":"2019-01-05T23:01:25.263Z","symbol":"XBTUSD","side":"Sell","size":30,"price":3801.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}
        """

        sell_trade_data2 = """
        {"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:00:1.000Z","symbol":"XBTUSD","side":"Sell","size":30,"price":3801.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}
        """


        db_loader = DbLoader()

        db_loader.open_db(':memory:')
        db_loader.load_line(partial_message)
        db_loader.load_line(update_message)
        db_loader.load_line(sell_trade_data)
        db_loader.load_line(sell_trade_data2)
        db_loader.load_line(data.funding_data)

        return db_loader.get_db()


    def test_message_to_list_zip(self):
        log_db = LogDb()

        message = [1000,2,3,400]

        m2 = log_db.list_to_zip_string(message)
        m3 = log_db.zip_string_to_list(m2)

        print ("row->", message, "zip->", m2, "unzip->", m3)
        assert(message == m3)





    def test_calc_center_price(self):
        db = LogDbTest.connect()

        price = db.calc_center_price(100, 100.5)
        assert(price == 100.5)

        price = db.calc_center_price(100, 101)
        assert(price == 100.5)

        price = db.calc_center_price(100, 101.5)
        assert(price == 101)

        price = db.calc_center_price(100, 102)
        assert(price == 101)



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

        print(db.select_order_book(1000))
        print(db.select_order_book(1001))

    pass

    @staticmethod
    def test_select_sell_trade():
        db = LogDbTest.connect()
        db.insert_sell_trade(1, 500, 1)

        print("selltrade->", db.select_sell_trade(1))
        pass

    @staticmethod
    def test_select_buy_trade():
        """
        :param time:
        :return: buy_trade list
        """
        db = LogDbTest.connect()
        print("buy_trade->", db.select_buy_trade(1))

    @staticmethod
    def test_select_funding():
        """
        :param time:
        :return: time_to_remain, funding_rate
        """
        db = LogDbTest.connect()
        print("funding->", db.select_funding(1))




if __name__ == '__main__':
    unittest.main()
