import numpy as np
from log.constant import *
import log.logdb as logdb;


TIME_WITH = 256
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

        self.sell_trade = np.zeros((TIME_WITH, BOOK_DEPTH))
        self.buy_trade = np.zeros((TIME_WITH, BOOK_DEPTH))
        self.sell_order = np.zeros((TIME_WITH, BOOK_DEPTH))
        self.buy_order = np.zeros((TIME_WITH, BOOK_DEPTH))
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
        p = int((price - self.center_price) / PRICE_UNIT + BOOK_DEPTH / 2)

        if p < 0 or BOOK_DEPTH <= p:
            return None

        return t, p


    def set_sell_order_book(self, time, price, line):
        width = 0
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos
            self.sell_order[t, p] = vol
            price += PRICE_UNIT
            width += 1
            if ORDER_BOOK_DATA_LIMIT < width:
                return

    def set_buy_order_book(self, time, price, line):
        width = 0
        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                return

            t, p = pos
            self.buy_order[t, p] = vol
            price -= PRICE_UNIT
            width += 1
            if ORDER_BOOK_DATA_LIMIT < width:
                return


    def add_buy_trade(self, time, price, volume, window = 1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.buy_trade[t][p] = self.buy_trade[t][p] + volume / window
            print(t, p, self.buy_trade[t][p])

    def add_sell_trade(self, time, price, volume, window = 1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.sell_trade[t][p] = self.sell_trade[t][p] + volume / window
            print(t, p, self.sell_trade[t][p])

    def set_funding(self, ttl, funding):

        print("fundig->", ttl, funding)

    def save(self, filename):
        #todo: not implemented
        print("---dummy---")
        #np.savez_compressed(filename, self.data)

    def calc_static(self, a):
        """
        calc matrix non zero mean and stddev
        :param a: matrix to be examine
        :return: mean, stddev
        """
        item_no = np.nonzero(a)[0].size
        non_zero_sum = np.sum(a)
        non_zero_sq_sum = np.sum(np.square(a))

        variant = non_zero_sq_sum / item_no - (non_zero_sum / item_no)**2

        return non_zero_sum/item_no, variant**0.5

    def normalize(self):
        order_mean, order_stddev = self.calc_static(self.sell_order + self.buy_order)

        trade_mean, trade_stddev = self.calc_static(self.sell_trade + self.buy_trade)

        print('ORDER stat->', order_mean, order_stddev)
        print('trade stat->', trade_mean, trade_stddev)

    def normalize_array(self, array, max_value):
        float_array = array * (256 / max_value)
        uint8_array = np.ceil(np.clip(float_array, 0, 255)).astype('uint8')

        print(uint8_array)

        return uint8_array



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
            #todo need tuning the window size
            if offset < 300:
                PriceBoard.load_from_db_time(db, board, time, offset)
            elif offset < 120:
                PriceBoard.load_from_db_time(db, board, time, offset, 8)
            elif offset < 180:
                PriceBoard.load_from_db_time(db, board, time, offset, 16)
            else:
                PriceBoard.load_from_db_time(db, board, time, offset, 32)

        return board



    @staticmethod
    def load_from_db_time(db, board, time_origin, offset = 0, magnifier = 1):
        query_time = time_origin - offset * magnifier
        #load sell order
        for t, price, volume in db.select_sell_trade(query_time, magnifier):
            board.add_sell_trade(time_origin - offset, price, volume)

        #load buy order
        for t, price, volume in db.select_buy_trade(query_time, magnifier):
            board.add_buy_trade(time_origin - offset, price, volume)

        #load order book
        order_book = None

        retry = 100
        if magnifier < retry:
            retry = magnifier + 50

        while(not order_book and retry):
            order_book = db.select_order_book(query_time - retry )
            retry = retry - 1

        if order_book:
            t, sell_min, sell_book, buy_max, buy_book = order_book
            board.set_sell_order_book(time_origin - offset, sell_min, sell_book)
            board.set_buy_order_book(time_origin - offset, buy_max, buy_book)
        else:
            print('---missing order book---', time_origin, query_time, retry)
