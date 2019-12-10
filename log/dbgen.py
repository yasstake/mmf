import os

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix
import tensorflow as tf
from matplotlib import pylab as plt

import log.logdb as logdb
from log.constant import *
from random import random


MAX_PRICE = 100000


class SparseBoard:
    def __init__(self, time_width=TIME_WIDTH, board_width=BOARD_WIDTH, max_price=MAX_PRICE):
        self.current_time = 0
        self.center_price = 0
        self.board_width = board_width

        self.board = None

        self.board = lil_matrix((board_width, max_price * 2), dtype=float)

    def get_board(self):
        pos = int((self.center_price * 2) - self.board_width / 2)
        return self.board[:, pos: pos + self.board_width]

    def roll(self):
        self.board = self._roll(self.board)

    def _roll(self, board):
        # todo: set axis , not imlemented
#        board = np.roll(board, axis=(0,), shift=1)

        #board[0, :] = 0
        return board

    def _pos(self, price):
        return int(price * 2)

    def add_order_vol(self, price, volume):
        self._add_order_vol(self.board, price, volume)

    def _add_order_vol(self, board, price, volume):
        p = self._pos(price)
        board[0, p] += volume

    def add_order_line(self, price, line, asc=True):
        self._add_order_line(self.board, price, line, asc)

    def _add_order_line(self, board, price, line, asc=True):
        p = self._pos(price)

        if asc:
            step = 1
        else:
            step = -1

        for vol in line:
            board[0, p] = vol
            p += step


class PriceBoard:
    """
    represent order book board and its history

    Layer 0   Buy order     (0 edge)
    Layer 1   Sell Order    (other side)
    Layer 2   Buy Trade & funding minus (0 edge)
    Layer 3   Sell Trade & funding plus (other side)

    """
    def __init__(self):
        self.current_time = 0
        self.center_price = 0

        self.sell_trade = SparseBoard()
        self.buy_trade = SparseBoard()
        self.sell_order = SparseBoard()
        self.buy_order = SparseBoard()

        self.buy_book_price = 0
        self.buy_book_vol = 0
        self.sell_book_price = 0
        self.sell_book_vol = 0

        self.sell_trade_price = 0
        self.sell_trade_volume = 0
        self.buy_trade_price = 0
        self.buy_trade_volume = 0

        self.my_sell_order = {}
        self.my_buy_order = {}

        self.market_sell_price = 0
        self.market_buy_price = 0

        self.fix_sell_price = 0
        self.fix_buy_price = 0

        self.funding_ttl = 0
        self.funding = 0

        self.best_action = ACTION.NOP
        self.ba_nop = 0
        self.ba_sell = 0
        self.ba_buy = 0
        self.ba_sell_now = 0
        self.ba_buy_now =0

    def next_tick(self):
        self.buy_trade.roll()
        self.sell_trade.roll()
        self.buy_order.roll()
        self.sell_order.roll()

    def get_board(self):
        order_mean, order_stddev = self.calc_static(self.sell_order + self.buy_order)
        trade_mean, trade_stddev = self.calc_static(self.sell_trade + self.buy_trade)

        buy_order = self.normalize_array(self.buy_order.get_board(), order_mean + order_stddev)
        sell_order = self.normalize_array(self.sell_order.get_board(), order_mean + order_stddev)

        buy_trade = self.normalize_array(self.buy_trade.get_board(), trade_mean + trade_stddev)
        sell_trade = self.normalize_array(self.sell_trade.get_board(), trade_mean + trade_stddev)

        board = np.stack([buy_order, sell_order, buy_trade, sell_trade])

        return board

    def set_origin_time(self, time):
        self.current_time = time

    def set_board_prices(self, sell_min, sell_vol, buy_max, buy_vol):
        self.sell_book_price = sell_min
        self.sell_book_vol = sell_vol
        self.buy_book_price = buy_max
        self.buy_book_vol = buy_vol

    def get_origin_time(self):
        return self.current_time

    def set_center_price(self, price):
        self.center_price = price

    def get_center_price(self):
        return self.center_price

    BOARD_CENTER = int(BOARD_WIDTH / 2)

    def set_sell_order_book(self, price, line):
        self.sell_order.add_order_line(price, line)

    def set_buy_order_book(self, price, line):
        self.buy_order.add_order_line(price, line, False)

    def add_buy_trade(self, price, volume):
        self.buy_trade.add_order_vol(price, volume)

    def add_sell_trade(self, price, volume):
        self.sell_trade.add_order_vol(price, volume)

    def set_funding(self, ttl, funding):
        print("fundig->", ttl, funding)
        self.funding = funding
        self.funding_ttl = ttl

    def calc_static(self, a):
        """
        calc matrix non zero mean and stddev
        :param a: matrix to be examine
        :return: mean, stddev
        """
        item_no = np.nonzero(a)[0].size
        non_zero_sum = np.sum(a)
        non_zero_sq_sum = np.sum(np.square(a))

        variant = non_zero_sq_sum / item_no - (non_zero_sum / item_no) ** 2

        return non_zero_sum/item_no, variant ** (0.5)

    def normalize_array(self, array, max_value):
        float_array = array * (256 / max_value)
        uint8_array = np.ceil(np.clip(float_array, 0, 255)).astype('uint8')

        return uint8_array


EPISODE_LEN = 60 * 60


class Generator:
    def __init__(self):
        self.db = None
        self.db_start_time = None
        self.db_end_time = None

    def create(self, time=None, db_name = "/tmp/bitlog.db"):
        if not self.db:
            self.open_db(db_name)

        if time is None:
            offset = int((self.db_end_time - self.db_start_time - EPISODE_LEN) * random()) + EPISODE_LEN
            print('offset->', offset)
            time = self.db_start_time + offset

        board = PriceBoard()
        retry = 10

        while True:
            time -= 1
            print('currenttime->', time)
            result = Generator.load_from_db(self.db, board, time)

            if result:
                yield board
                board.next_tick()
            else:
                retry -= 1
                if not retry:
                    break

        yield None

    def open_db(self, db_name):
        self.db = logdb.LogDb(db_name)
        self.db.connect()
        self.db.create_cursor()
        self.db_start_time, self.db_end_time = Generator.start_time(self.db)
        print('OPENDB->', db_name, self.db_start_time, self.db_end_time)

    def close_db(self):
        if self.db:
            self.db.close()

    @staticmethod
    def start_time(db=None):
        if db is None:
            db = logdb.LogDb('/tmp/bitlog.db')
            db.connect()
            db.create_cursor()

        start_time, end_time = db.get_db_info()
        start_time += TIME_WIDTH * 2

        return start_time, end_time

    @staticmethod
    def load_from_db(db, board, time):
        board.set_origin_time(time)

        result = db.select_book_price(time)
        if result:
            sell_min, sell_volume, buy_max, buy_volume = result
        else:
            print('---DBEND---(center_book price)')
            return None

        center_price = db.calc_center_price(buy_max, sell_min)
        if not center_price:
            print('---DBEND---(center_price)')
            return None

        board.set_center_price(center_price)
        board.set_board_prices(sell_min, sell_volume, buy_max, buy_volume)

        '''
        #load funding
        funding = db.select_funding(time)

        if funding:
            t, p = funding
            board.funding_ttl = 0
            board.funding = 0
        else:
            print('---DBEND---(funding)')
            return None
        '''

        # load sell order
        for price, volume in db.select_sell_trade(time):
            board.add_sell_trade(price, volume)

        # load buy order
        for price, volume in db.select_buy_trade(time):
            board.add_buy_trade(price, volume)

        order_book = db.select_order_book(time)

        if order_book:
            t, sell_min, sell_book, buy_max, buy_book = order_book
            board.set_sell_order_book(sell_min, sell_book)
            board.set_buy_order_book(buy_max, buy_book)
        else:
            print("NO ORDERBOOK FOUND->", time)
            return False

        return True

