import os

import numpy as np
import tensorflow as tf
from matplotlib import pylab as plt

import log.logdb as logdb
from log.constant import *
from log.timeutil import *
from log.price import PriceBoard
from random import random


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
