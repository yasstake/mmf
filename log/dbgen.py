import os

import numpy as np
import tensorflow as tf
from matplotlib import pylab as plt

import log.logdb as logdb
from log.constant import *
from log.timeutil import *
from log.price import PriceBoard
from random import random
from scipy.sparse import csr_matrix

MAX_PRICE = 200000


class SparseBoard:
    def __init__(self, time_width=TIME_WIDTH, board_width=BOARD_WIDTH, max_price=MAX_PRICE):
        self.current_time = 0
        self.center_price = 0
        self.board_width = board_width

        self.board = csr_matrix((time_width, max_price), dtype=float)

    def get_board(self):
        pos = int((self.center_price * 2) - self.board_width)
        return self.board[:, pos: pos + self.board_width]

    def roll(self):
        self.board = self._roll(self.board)

    def _roll(self, board):
        board = np.roll(board, axis=0, shift=1)
        board[0, :] = 0
        return board

    def add_order_vol(self, price, volume):
        self._add_order_vol(self.board, price, volume)

    def _pos(self, price):
        return int(price * 2)

    def _add_order_vol(self, board, price, volume):
        p = self._pos(price)
        board[0, p] += volume

    def add_order_line(self, board, price, line, asc=True):
        self.add_order_line(self.board, price, line, asc)

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

        self.sell_trade = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.buy_trade = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.sell_order = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.buy_order = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))

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

    def get_board(self):
        board = np.stack([self.buy_order, self.sell_order, self.buy_trade, self.sell_trade])
        return board

#    def add_sell_order(self, price, size):
#        if price in self.my_sell_order:
#            self.my_sell_order[price] += size
#        else:
#            self.my_sell_order[price] = size

#    def add_buy_order(self, price, size):
#        if price in self.buy_order:
#            self.my_buy_order[price] += size
#        else:
#            self.my_buy_order[price] = size

    def set_origin_time(self,time):
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

    BOARD_CENTER = BOARD_WIDTH / 2

    def get_position(self, time, price):
        p = int((price - self.center_price) / PRICE_UNIT + PriceBoardDB.BOARD_CENTER)

        if p < 0 or BOARD_WIDTH <= p:
            return None

        t = int(self.current_time - time + 1) # first line for my order

        return t, p

    def set_sell_order_book(self, time, price, line):
        width = 0

        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                break

            t, p = pos
            self.sell_order[t, p] = vol
            price += PRICE_UNIT
            width += 1

            if BOARD_WIDTH < width:
                break

    def set_buy_order_book(self, time, price, line):
        width = 0

        for vol in line:
            pos = self.get_position(time, price)

            if not pos:
                break

            t, p = pos
            self.buy_order[t, p] = vol

            price -= PRICE_UNIT
            width += 1
            if BOARD_WIDTH < width:
                break

    def add_buy_trade(self, time, price, volume, window=1):
        if time == self.current_time:
            if self.buy_trade_price == 0:
                self.buy_trade_price = price

            if self.buy_trade_price == price:
                self.buy_trade_volume += volume

        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.buy_trade[t][p] = self.buy_trade[t][p] + volume / window

    def add_sell_trade(self, time, price, volume, window=1):
        if time == self.current_time:
            if self.sell_trade_price == 0:
                self.sell_trade_price = price

            if self.sell_trade_price == price:
                self.sell_trade_volume += volume

        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.sell_trade[t][p] = self.sell_trade[t][p] + volume / window

    def set_funding(self, ttl, funding):
        print("fundig->", ttl, funding)
        self.funding = funding
        self.funding_ttl = ttl

    def save(self, filename):
        #todo: not implemented
        print("---dummy---")
        np.save(filename + "sell_order", self.sell_order)
        np.save(filename + "buy_order", self.buy_order)
        np.save(filename + "buy_trade", self.buy_trade)
        np.save(filename + "sell_trade", self.sell_trade)

        np.savez_compressed(filename + "sell_order", self.sell_order)
        np.savez_compressed(filename + "buy_order", self.buy_order)
        np.savez_compressed(filename + "buy_trade", self.buy_trade)
        np.savez_compressed(filename + "sell_trade", self.sell_trade)

        #np.savez_compressed(filename, self.data)

    def feature_int64(self, a):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[a]))

    def feature_float(self, a):
        return tf.train.Feature(float_list=tf.train.FloatList(value=[a]))

    def feature_bytes(self, a):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[a]))

    @staticmethod
    def get_tf_writer(output_file='/tmp/data.tfrecords'):
        writer = tf.io.TFRecordWriter(str(output_file), options=tf.io.TFRecordOptions(tf.io.TFRecordCompressionType.GZIP))

        return writer

    def save_tf_record(self, output_file='/tmp/data.tfrecords'):
        writer = PriceBoard.get_tf_writer(output_file)
        self.save_tf_to_writer(writer)
        writer.close()

    def save_tf_to_writer(self, writer):
        record = self._tf_example_record()

        writer.write(record.SerializeToString())

    def _tf_example_record(self):
        board = np.stack([self.buy_order, self.sell_order, self.buy_trade, self.sell_trade])

        record = tf.train.Example(features=tf.train.Features(feature={
            'board': self.feature_bytes(board.tobytes()),
            'sell_book_price': self.feature_float(self.sell_book_price),
            'sell_book_vol': self.feature_float(self.sell_book_vol),
            'buy_book_price': self.feature_float(self.buy_book_price),
            'buy_book_vol': self.feature_float(self.buy_book_vol),
            'center_price': self.feature_float(self.center_price),
            'sell_trade_price': self.feature_float(self.sell_trade_price),
            'sell_trade_vol': self.feature_float(self.sell_trade_volume),
            'buy_trade_price': self.feature_float(self.buy_trade_price),
            'buy_trade_vol': self.feature_float(self.buy_trade_volume),
            'market_buy_price': self.feature_float(self.market_buy_price),
            'market_sell_price': self.feature_float(self.market_sell_price),
            'fix_buy_price': self.feature_float(self.fix_buy_price),
            'fix_sell_price': self.feature_float(self.fix_sell_price),
            'ba': self.feature_int64(self.best_action),
            'ba_nop': self.feature_int64(self.ba_nop),
            'ba_sell': self.feature_int64(self.ba_sell),
            'ba_buy': self.feature_int64(self.ba_buy),
            'ba_sell_now': self.feature_int64(self.ba_sell_now),
            'ba_buy_now': self.feature_int64(self.ba_buy_now),
            'time': self.feature_int64(self.current_time)
            }))

        return record

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

    def normalize(self):
        order_mean, order_stddev = self.calc_static(self.sell_order + self.buy_order)
        trade_mean, trade_stddev = self.calc_static(self.sell_trade + self.buy_trade)

        self.buy_order = self.normalize_array(self.buy_order, order_mean + order_stddev)
        self.sell_order = self.normalize_array(self.sell_order, order_mean + order_stddev)

        self.buy_trade = self.normalize_array(self.buy_trade, trade_mean + trade_stddev)
        self.sell_trade = self.normalize_array(self.sell_trade, trade_mean + trade_stddev)

    def normalize_array(self, array, max_value):
        float_array = array * (256 / max_value)
        uint8_array = np.ceil(np.clip(float_array, 0, 255)).astype('uint8')

        return uint8_array


class Generator:
    def __init__(self):
        self.db = None
        self.db_start_time = None
        self.db_end_time = None

    def create(self, time=None, db_name = "/tmp/bitlog.db"):
        if not self.db:
            self.open_db(db_name)

        if time is None:
            offset = int((self.db_end_time - self.db_start_time) * random())
            time = self.db_start_time + offset

        while True:
            board = Generator._load_from_db(self.db, time)
            time += 1
            if not board:
                break
            yield board
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
    def _load_from_db(dbobj, time, time_width=TIME_WIDTH):
        db = dbobj
        board = PriceBoard()
        board.set_origin_time(time)

        retry = 1
        center_price = None
        sell_min = None
        sell_volume = None
        buy_max = None
        buy_volume = None

        while retry:
            result = db.select_book_price(time)
            if result:
                sell_min, sell_volume, buy_max, buy_volume = result
            else:
                return None

            center_price = db.calc_center_price(buy_max, sell_min)
            if center_price:
                break
            time = time + 1
            retry = retry - 1

        if not center_price:
            print('---DBEND---')
            return None

        board.set_center_price(center_price)
        board.set_board_prices(sell_min, sell_volume, buy_max, buy_volume)

        error_count = 0
        query_time = time

        for offset in range(0, time_width):
            if not Generator.load_from_db_time(db, board, time, offset, query_time):
                error_count = error_count + 1
            query_time = query_time - 1

        board.normalize()

        #load funding
        funding = db.select_funding(time)

        if funding:
            t, p = funding
            board.funding_ttl = 0
            board.funding = 0

        if 10 < error_count:
            return None

        return board

    @staticmethod
    def load_from_db_time(db, board, time_origin, offset, query_time, time_window=1):

        # load sell order
        for price, volume in db.select_sell_trade(query_time, time_window):
            board.add_sell_trade(time_origin - offset, price, volume / time_window)

        # load buy order
        for price, volume in db.select_buy_trade(query_time, time_window):
            board.add_buy_trade(time_origin - offset, price, volume / time_window)

        # load order book
        order_book = None

        max_retry = 10
        if time_window < max_retry:
            max_retry = time_window + 50

        retry = 0
        while not order_book and retry < max_retry:
            order_book = db.select_order_book(query_time - retry)
            retry = retry + 1

        if order_book:
            t, sell_min, sell_book, buy_max, buy_book = order_book
            board.set_sell_order_book(time_origin - offset, sell_min, sell_book)
            if(len(sell_book) < 10):
                print("shot->", time_origin - offset, sell_book)

            board.set_buy_order_book(time_origin - offset, buy_max, buy_book)

            return True
        else:
            print("NO ORDERBOOK FOUND->", query_time)
            return False
