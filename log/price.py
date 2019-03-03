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
        #        self.data = np.zeros((TIME_WITH, PRICE_HEIGHT,NUMBER_OF_LAYERS))

        self.sell_trade = np.zeros((TIME_WITH, PRICE_HEIGHT))
        self.buy_trade = np.zeros((TIME_WITH, PRICE_HEIGHT))
        self.sell_order = np.zeros((TIME_WITH, PRICE_HEIGHT))
        self.buy_order = np.zeros((TIME_WITH, PRICE_HEIGHT))
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
        t = int(self.current_time - time)
        p = int((price - self.center_price) / PRICE_UNIT + PRICE_HEIGHT / 2)

        if p < 0 or PRICE_HEIGHT <= p:
            return None

        return t, p


    def set_sell_order_book(self, time, price, line):
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos
            self.sell_order[t, p] = vol
            price += PRICE_UNIT

    def set_buy_order_book(self, time, price, line):
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos
            self.buy_order[t, p] = vol
            price -= PRICE_UNIT

    def add_buy_trade(self, time, price, volume, window = 1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.buy_trade[t][p] = self.buy_trade[t][p] + volume / window

    def add_sell_trade(self, time, price, volume, window = 1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.sell_trade[t][p] = self.sell_trade[t][p] + volume / window

    def set_funding(self, ttl, funding):
        print("fundig->", ttl, funding)

    def save(self, filename):
        #todo: not implemented
        print("---dummy---")
        #np.savez_compressed(filename, self.data)

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

        for offset in range(0,TIME_WITH):
            PriceBoard.load_from_db_time(db, board, time, offset)

#            if offset < 60:

#            elif offset < 120:
 #               PriceBoard.load_from_db_time(db, board, time, offset*2, 2)
#            elif offset < 180:
#n                PriceBoard.load_from_db_time(db, board, time, offset*4, 4)
#            else:
#                PriceBoard.load_from_db_time(db, board, time, offset*8, 8)

        return board



    @staticmethod
    def load_from_db_time(db, board, time_origin, offset = 0, magnifier = 1):
        #load sell order
        for t, price, volume in db.select_sell_trade(time_origin - offset, magnifier):
            board.add_sell_trade(time_origin - offset, price, volume)

        #load buy order
        for t, price, volume in db.select_buy_trade(time_origin - offset, magnifier):
            board.add_buy_trade(time_origin - offset, price, volume)

        #load order book
        order_book = None
        retry = 3
        while(not order_book and retry):
            order_book = db.select_order_book(time_origin - retry - offset)
            retry = retry - 1

        if order_book:
            print("--order-book")
            t, sell_min, sell_book, buy_max, buy_book = order_book
            board.set_sell_order_book(time_origin - offset, sell_min, sell_book)
            board.set_buy_order_book(time_origin - offset, buy_max, buy_book)

