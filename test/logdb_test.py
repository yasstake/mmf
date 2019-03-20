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

        sell_trade_data = """{"table":"trade","action":"insert","data":[{"timestamp":"2019-01-05T23:01:25.263Z","symbol":"XBTUSD","side":"Sell","size":30,"price":3801.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""

        sell_trade_data2 = """
        {"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:00:1.000Z","symbol":"XBTUSD","side":"Sell","size":30,"price":3801.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}
        """
        sell_trade_data01 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:49.00Z","symbol":"XBTUSD","side":"Sell","size":5,"price":99.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data02 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:50.00Z","symbol":"XBTUSD","side":"Sell","size":5,"price":99.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data03 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:51.00Z","symbol":"XBTUSD","side":"Sell","size":5,"price":99.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data04 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:52.00Z","symbol":"XBTUSD","side":"Sell","size":1,"price":99,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data05 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:53.00Z","symbol":"XBTUSD","side":"Sell","size":30,"price":99,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data06 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:49.00Z","symbol":"XBTUSD","side":"Buy","size":5,"price":99.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data07 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:50.00Z","symbol":"XBTUSD","side":"Buy","size":5,"price":99,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data08 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:51.00Z","symbol":"XBTUSD","side":"Buy","size":5,"price":99,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data09 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:52.00Z","symbol":"XBTUSD","side":"Buy","size":5,"price":97,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data10 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:53.00Z","symbol":"XBTUSD","side":"Buy","size":5,"price":96,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data11 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:54.00Z","symbol":"XBTUSD","side":"Buy","size":6,"price":95,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data12 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:49.00Z","symbol":"XBTUSD","side":"Buy","size":30,"price":94,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data13 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:49.00Z","symbol":"XBTUSD","side":"Buy","size":30,"price":94,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""
        sell_trade_data14 = """{"table":"trade","action":"insert","data":[{"timestamp":"1970-01-01T00:16:49.00Z","symbol":"XBTUSD","side":"Buy","size":30,"price":94,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}"""



        db_loader = DbLoader()

        db_loader.open_db(':memory:')
        db_loader.load_line(partial_message)
        db_loader.load_line(update_message)
        db_loader.load_line(sell_trade_data)
        db_loader.load_line(sell_trade_data2)
        db_loader.load_line(data.funding_data)
        db_loader.load_line(sell_trade_data01)
        db_loader.load_line(sell_trade_data02)
        db_loader.load_line(sell_trade_data03)
        db_loader.load_line(sell_trade_data04)
        db_loader.load_line(sell_trade_data05)
        db_loader.load_line(sell_trade_data06)
        db_loader.load_line(sell_trade_data07)
        db_loader.load_line(sell_trade_data08)
        db_loader.load_line(sell_trade_data09)
        db_loader.load_line(sell_trade_data10)
        db_loader.load_line(sell_trade_data11)
        db_loader.load_line(sell_trade_data12)
        db_loader.load_line(sell_trade_data13)
        db_loader.load_line(sell_trade_data14)
#        db_loader.load_line(sell_trade_data15)
#        db_loader.load_line(sell_trade_data16)



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

        price = db.calc_center_price(50, 51)
        assert(price == 50.5)



    @staticmethod
    def test_select_center_price():
        db = LogDbTest.connect()

        time_org = 1000

        center_price = db.select_center_price(time_org)

        print("CenterPrice->", center_price)
        assert(center_price == 50.5)

        center_price = db.select_center_price(1001)
        print(center_price)
        assert(center_price == 99.5)

        center_price = db.select_center_price(100000) #not exist in db
        print(center_price)


    @staticmethod
    def test_select_order_book():

        db = LogDbTest.connect()

        print("select order book->")
        print("1000->")
        print(db.select_order_book(1000))
        print("1001->")
        print(db.select_order_book(1001))
        print("1->")
        print(db.select_order_book(1))


    @staticmethod
    def test_select_sell_trade():
        db = LogDbTest.connect()
        db.insert_sell_trade(1, 500, 1)

        print("selltrade->", db.select_sell_trade(1))
        print("selltrade->", db.select_sell_trade(2))
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

        rec = db.select_funding(1)

        if rec:
            ttl, funding = rec
            print("funding->", ttl, funding)
        else:
            print("funding -none")


    def test_order_book_price(self):
        db = LogDbTest.connect()
        rec = db.select_order_book_price(1000)

        sell_min, sell_volume, buy_max, buy_volume = rec

        self.assertEqual(sell_min, 51)
        self.assertEqual(sell_volume, 10)
        self.assertEqual(buy_max, 50)
        self.assertEqual(buy_volume, 10)

    def test_calc_market_buy_price(self):
        db = LogDbTest.connect()

        price = db.calc_market_order_buy(1000, 1)  # enough small
        self.assertEqual(price, 51)

        price = db.calc_market_order_buy(1000, 1000)  # too big, rise the price PRICE_UNIT * 2
        self.assertEqual(price, 52)


    def test_calc_market_sell_price(self):
        db = LogDbTest.connect()

        price = db.calc_market_order_sell(1000, 1)  # enough small
        self.assertEqual(price, 50)

        price = db.calc_market_order_sell(1000, 1000)  # too big, rise the price PRICE_UNIT * 2
        self.assertEqual(price, 49)

    def test_is_suceess_fixed_order_sell(self):
        db = LogDbTest.connect()

        result = db.is_suceess_fixed_order_sell(1000, 99, 1)
        self.assertEqual(result, True)

        result = db.is_suceess_fixed_order_sell(1000, 99, 100)
        self.assertEqual(result, False)

        result = db.is_suceess_fixed_order_sell(1000, 100, 1)
        self.assertEqual(result, False)


    def test_is_suceess_fixed_order_buy(self):
        db = LogDbTest.connect()

        result = db.is_suceess_fixed_order_buy(1000, 98, 1)
        self.assertEqual(result, False)

        result = db.is_suceess_fixed_order_buy(1000, 99, 1)
        self.assertEqual(result, True)

        result = db.is_suceess_fixed_order_buy(1000, 99.5, 1)
        self.assertEqual(result, True)

        result = db.is_suceess_fixed_order_buy(1000, 99.5, 100)
        self.assertEqual(result, False)

    def test_calc_fixed_buy_order_price(self):
        db = LogDbTest.connect()

        price = db._calc_order_book_price_buy(1000)
        self.assertEqual(50, price)

        price = db._calc_order_book_price_buy(1001)
        self.assertEqual(99, price)


    def test_calc_fixed_sell_order_price(self):
        db = LogDbTest.connect()

        result = db._calc_order_book_price_sell(1000)
        self.assertEqual(result, 51)

        result = db._calc_order_book_price_sell(1001)
        self.assertEqual(result, 99.5)


    def test_calc_fixed_order_sell(self):
        db = LogDbTest.connect()

        board_price = db._calc_order_book_price_sell(1001)
        print(board_price)

        price = db.calc_fixed_order_sell(1001, 1)
        self.assertEqual(price, 99.5)

        price = db.calc_fixed_order_sell(1001, 1000)
        self.assertEqual(price, None)



    def test_calc_fixed_order_buy(self):
        db = LogDbTest.connect()

        board_price = db._calc_order_book_price_buy(1001)
        print(board_price)

        price = db.calc_fixed_order_buy(1001, 1)
        self.assertEqual(price, 99)

        price = db.calc_fixed_order_buy(1001, 1000)
        self.assertEqual(price, None)


    def test_calc_fixed_order_sell(self):
        db = LogDbTest.connect()

        board_price = db._calc_order_book_price_sell(1001)
        print(board_price)

        price = db.calc_fixed_order_sell(1001, 1)
        self.assertEqual(price, 99.5)

        price = db.calc_fixed_order_sell(1001, 1000)
        self.assertEqual(price, None)

    def test_calc_market_order_buy(self):
        db = LogDbTest.connect()

        price = db.calc_market_order_buy(1001, 1)
        self.assertEqual(price, 99.5)

        price = db.calc_market_order_buy(1001, 1000)
        self.assertEqual(price, 100.5) # up 2 tick = 1

    def test_calc_market_order_sell(self):
        db = LogDbTest.connect()

        price = db.calc_market_order_sell(1001, 1)
        self.assertEqual(price, 99)

        price = db.calc_market_order_sell(1001, 1000)
        self.assertEqual(price, 98) # down 2 tick = 1




    def test_select_times(self):
        db = LogDbTest.connect()

        db.update_all_order_prices()

    def test_load_db(self):
        db = LogDbTest.connect()
        db.import_db()

    def test_copy_db(self):
        db = LogDbTest.connect()
        #db.copy_db("/tmp/bitlog.db", "/tmp/export.db", 1552712400, 7)
        db.copy_db("/tmp/bitlog.db", "/tmp/export.db", 0, 1552712400)

    def test_db_info(self):
        db = LogDb("/tmp/bitlog.db")
        db.connect()

        db.get_db_info()

if __name__ == '__main__':
    unittest.main()
