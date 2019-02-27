import numpy as np
from log.constant import *
import log.logdb as logdb;


TIME_WITH = 256
PRICE_HEIGHT = 256
NUMBER_OF_LAYERS = 4


class PriceBoard():
    """
    represent order book board and its history

    Layer 1   Buy order
    Layer 2   Sell Order
    Layer 3   Buy Trade
    Layer 4   Sell Trade

    """
    def __init__(self):
        self.data = np.zeros((TIME_WITH, PRICE_HEIGHT,NUMBER_OF_LAYERS))
        self.current_time = 0
        self.center_price = 0

    def set_origin_time(self,time):
        self.current_time = time

    def get_origin_time(self):
        return self.current_time

    def set_center_price(self, price):
        self.center_price = price

    def get_center_price(self):
        return self.center_price

    def get_position(self, time, price):
        t = self.current_time - time
        p = int((price - self.center_price) / PRICE_UNIT + PRICE_HEIGHT / 2)

        return t, p


    def set_sell_order_book(self, time, price, line):
        pass

    def set_buy_order_book(self, time, price, line):
        pass

    def set_buy_trade(self, time, price, volume):
        pass

    def set_sell_trade(self, time, price, volume):
        pass


    def save(self, filename):
        np.savez_compressed(filename, self.data)

    @staticmethod
    def load_from_db(time, db_name = "/tmp/bitlog.db"):
        db = logdb.LogDb(db_name)
        db.connect()

        center_price = db.select_center_price(time)
        print(center_price)

        board = PriceBoard()
        board.set_center_price(center_price)
        board.set_origin_time(time)


