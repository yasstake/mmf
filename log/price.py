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

        if p < 0 or PRICE_HEIGHT <= p:
            return None

        return t, p


    def set_sell_order_book(self, time, price, line):
        print("sell_orderbook", time, " ", price, " ", line)
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos

            self.data[t, p, 0] = vol
            print("sell", t, " ", p, " ", vol)
            price += PRICE_UNIT

    def set_buy_order_book(self, time, price, line):
        print("buy_orderbook", time, " ", price, " ", line)
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos

            self.data[t, p, 1] = vol

            print("buy", t, " ", p, " ", vol)
            price -= PRICE_UNIT

    def add_buy_trade(self, time, price, volume):
        print("buy-trade", time, price, volume)


    def add_sell_trade(self, time, price, volume):
        print("sell-trade", time, price, volume)

    def set_funding(self, ttl, funding):
        print("fundig->", ttl, funding)

    def save(self, filename):
        np.savez_compressed(filename, self.data)

    @staticmethod
    def load_from_db(time, db_name = "/tmp/bitlog.db"):
        db = logdb.LogDb(db_name)
        db.connect()
        board = PriceBoard()

        board.set_origin_time(time)
        print("origin->", board.get_origin_time())

        center_price = db.select_center_price(time)
        board.set_center_price(center_price)
        print("centerPrice->", board.get_center_price())

        #load funding
        funding = db.select_funding(time)

        if funding:
            t, p = funding
            board.set_funding(t, p)

        PriceBoard.load_from_db_time(db, board, time)

        return board

    @staticmethod
    def load_from_db_time(db, board, time):
        #load sell order
        for time, price, volume in db.select_sell_trade(time):
            board.add_sell_order(time, price, volume)

        #load buy order
        for time, price, volume in db.select_buy_trade(time):
            board.add_buy_order(time, price, volume)

        #load order book
        order_book = db.select_order_book(time)

        if order_book:
            time, sell_min, sell_book, buy_max, buy_book = order_book

            board.set_sell_order_book(time, sell_min, sell_book)
            board.set_buy_order_book(time, buy_max, buy_book)
