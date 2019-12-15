import os

import numpy as np
import tensorflow as tf
from matplotlib import pylab as plt

import log.logdb as logdb
from log.constant import *
from random import random

MAX_PRICE = 100000


class SparseLine:
    def __init__(self):
        self.start_index = 0
        self.last_index = 0
        self.line = np.zeros(0)

    def set_line(self, start_index,  line, asc=True):

        if asc:
            self.line = np.array(line)
            self.start_index = start_index
            self.last_index = start_index + len(line)
        else:
            self.line = np.array(line[::-1])
            self.start_index = start_index - len(line) + 1
            self.last_index = start_index + 1

    def get_line(self, start_clip, end_clip):
        '''
         self.start_index              self.last_index
         [0]                           [len(self.line)]
         |                             |
        [x, x, x, x, x, x, x, x, x, x, x]
        :param start_clip:
        :param end_clip:
        :return:
        '''

        clip = None

        # (SC <  si) < [li < EC]
        if (start_clip <= self.start_index) and (self.last_index <= end_clip):
            zero1 = self.start_index - start_clip
            zero2 = end_clip - self.last_index
            clip = np.append(np.zeros(zero1), self.line)
            clip = np.append(clip, np.zeros(zero2))

        # (si < SC) < (EC  <  li)
        elif (self.start_index <= start_clip) and (end_clip <= self.last_index):
            clip = np.array(self.line[start_clip - self.start_index : end_clip - self.start_index])

        # (SC <  [si) < EC] <  li
        elif (start_clip <= self.start_index) and (self.start_index <= end_clip):
            zeros = self.start_index - start_clip
            end = end_clip - self.start_index
            clip = np.append(np.zeros(zeros), self.line[:end])

        # si < (SC < [li) < EC]
        elif (start_clip < self.last_index) and (self.last_index <= end_clip):
            start = start_clip - self.start_index
            zeros = end_clip - self.last_index
            clip = np.append(self.line[start:], np.zeros(zeros))

        # si <  (li < SC) < EC  or
        # SC <  (EC < si) < li
        elif (self.last_index <= start_clip) or (end_clip <= self.start_index):
            clip = np.zeros(end_clip - start_clip)
        else:
            print('clip error', start_clip, end_clip, self.start_index, self.last_index)

        return clip

    def check_and_extend_array(self, index):
        if (self.start_index <= index) and (index < self.last_index):
            return True
        if self.start_index == 0 and self.last_index == 0:
            self.start_index = index
            self.last_index = index + 1
            self.line = np.zeros(1)
            return True
        elif index < self.start_index:
            self.line = np.insert(self.line, 0, np.zeros(self.start_index - index))
            self.start_index = index
            return True
        elif self.last_index <= index:
            size = index + 1 - self.last_index
            self.last_index = index + 1

            self.line = np.append(self.line, np.zeros(size))
            return True

        print('error extend index', index)
        return False

    def add_value(self, index, value):
        self.check_and_extend_array(index)

        pos = index - self.start_index

        if len(self.line) < pos:
            print('error in pos', index, value, len(self.line), self.start_index, self.last_index)

        self.line[pos] += value

    def get_value(self, index):
        return self.line[index - self.start_index]


class SparseMatrix:
    def __init__(self, time_width=TIME_WIDTH):
        self.time_len = time_width
        self.center_price = 0

        self.array = []
        for i in range(self.time_len):
            self.array.append(SparseLine())

    def roll(self, copy_last_line=False):
        if copy_last_line:
            sparse_line = self.array[-1]  # shift recycle
        else:
            sparse_line = SparseLine()  # new

        self.array = self.array[1:]
        self.array.append(sparse_line)

    def set_line(self, start_price, line, asc=True):
        pos = self.price_pos(start_price)
        self.array[-1].set_line(pos, line, asc)

    def get(self, start_index, end_index):
        price_array = []

        for i in range(self.time_len):
            price_array.append(self.array[i].get_line(start_index, end_index))

        return np.array(price_array)

    def get_board(self, start=None, board_width=BOARD_WIDTH):
        offset = int(board_width / 2)

        if not start:
            start = self.price_pos(self.center_price) - offset

        end = start + board_width

        return self.get(start, end)

    def add_value(self, price, value):
        pos = self.price_pos(price)
        self.array[-1].add_value(pos, value)

    def price_pos(self, price):
        return int(price * 2)


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

        self.sell_trade = SparseMatrix()
        self.buy_trade = SparseMatrix()
        self.sell_order = SparseMatrix()
        self.buy_order = SparseMatrix()

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

        # sell simulation result
        self.market_sell_price = None
        self.market_buy_price = None
        self.fix_sell_price = None
        self.fix_sell_price_time = None
        self.fix_buy_price = None
        self.fix_buy_price_time = None

        self.funding_ttl = 0
        self.funding = 0

    def next_tick(self, copy_last_data=False):
        self.buy_trade.roll(copy_last_data)
        self.sell_trade.roll(copy_last_data)
        self.buy_order.roll(copy_last_data)
        self.sell_order.roll(copy_last_data)

    def get_std_boards(self):
        sell_order = self.sell_order.get_board()
        buy_order = self.buy_order.get_board()
        buy_trade = self.buy_trade.get_board()
        sell_trade = self.sell_trade.get_board()

        order_mean, order_stddev = self.calc_static(sell_order + buy_order)
        trade_mean, trade_stddev = self.calc_static(sell_trade + buy_trade)

        buy_order = self.normalize_array(buy_order, order_mean + order_stddev)
        sell_order = self.normalize_array(sell_order, order_mean + order_stddev)

        buy_trade = self.normalize_array(buy_trade, trade_mean + trade_stddev)
        sell_trade = self.normalize_array(sell_trade, trade_mean + trade_stddev)

        boards = buy_order, sell_order, buy_trade, sell_trade

        return boards

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

        self.sell_order.center_price = self.center_price
        self.buy_order.center_price = self.center_price
        self.buy_trade.center_price = self.center_price
        self.sell_trade.center_price = self.center_price

    def get_center_price(self):
        return self.center_price

    BOARD_CENTER = int(BOARD_WIDTH / 2)

    def price_offset(self, price):
        pos = self.buy_order.price_pos(price) - self.center_price - PriceBoard.BOARD_CENTER

        if pos < 0:
            pos = 0
        elif BOARD_WIDTH < pos:
            pos = BOARD_WIDTH

        return int(pos)

    def set_sell_order_book(self, price, line):
        self.sell_order.set_line(price, line)

    def set_buy_order_book(self, price, line):
        self.buy_order.set_line(price, line, False)

    def add_buy_trade(self, price, volume):
        self.buy_trade.add_value(price, volume)

    def add_sell_trade(self, price, volume):
        self.sell_trade.add_value(price, volume)

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

        return non_zero_sum/item_no, variant ** 0.5

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
        self.time = None

    def create(self, time=None, db_name = "/tmp/bitlog.db"):
        if not self.db:
            self.open_db(db_name)

        if time is None:
            offset = int((self.db_end_time - self.db_start_time - EPISODE_LEN) * random()) + EPISODE_LEN
            time = self.db_start_time + offset

        self.time = time

        board = PriceBoard()

        time_len = BOARD_TIME_WIDTH

        # fill data
        while time_len:
            Generator.load_from_db(self.db, board, self.time)
            self.time += 1
            board.next_tick()
            time_len -= 1
        retry = 10

        while True:
            result = Generator.load_from_db(self.db, board, self.time)
            self.time += 1
            if result:
                yield board
                board.next_tick()
                retry = 10
            else:
                retry -= 1
                if not retry:
                    break

        print('[DBEND]')
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
            print('[' + str(time) + ' skip]', end='')
            return None

        center_price = db.calc_center_price(buy_max, sell_min)
        if not center_price:
            print('[' + str(time) + ']' + 'missing info(center_price)', end='')
            return None

        board.set_center_price(center_price)
        board.set_board_prices(sell_min, sell_volume, buy_max, buy_volume)

        #load funding
        '''
        funding = db.select_funding(time)

        if funding:
            t, p = funding
            board.funding_ttl = 0
            board.funding = 0
        else:
            print('---DBEND---(funding)')
            return None
        '''

        # load fix order prices
        result = db.select_expected_price_with_time(time)
        if result:
            market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time, fix_order_buy, fix_order_buy_time = result

            board.market_sell_price = market_order_sell
            board.market_buy_price = market_order_buy
            board.fix_sell_price = fix_order_sell
            board.fix_sell_price_time = fix_order_sell_time
            board.fix_buy_price = fix_order_buy
            board.fix_buy_price_time = fix_order_buy_time

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
