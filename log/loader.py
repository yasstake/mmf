import gzip
import json
import logging

import log.encoder
from log.constant import *
from log.timeutil import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class LogLoader:
    def __init__(self, order_book_tick = None, trade_tick = None, funding_tick = None):
        self.order_book_tick = order_book_tick
        self.trade_tick = trade_tick
        self.funding_tick = funding_tick

        # order book
        self.data_hash = dict()

        self.time_stamp = 0
        self.ready = False

        # funding
        self.funding_time = None
        self.funding_rate = None

        #trade infomation
        self.trade_time = None
        self.trade_sell = {}
        self.trade_buy  = {}

    @staticmethod
    def message_to_list(message):
        sell_min = 999999999
        sell = {}
        sell_vol = 0

        buy_max = 0
        buy = {}
        buy_vol = 0

        for item in message:
            volume = item['size']
            price = item['price']

            if item['side'] == 'Sell':
                sell[price] = volume
                if price < sell_min:
                    sell_min = price
                    sell_vol = volume
            else:
                buy[price] = volume
                if buy_max < price:
                    buy_max = price
                    buy_vol = volume

        buy_list = []
        for i in range(BOOK_DEPTH):
            index = buy_max - i * PRICE_UNIT
            if index in buy:
                buy_list.append(buy[index])

        sell_list = []
        for i in range(BOOK_DEPTH):
            index = sell_min + i * PRICE_UNIT
            if index in sell:
                sell_list.append(sell[index])

        return sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list

    def on_message(self, message):
        message = json.loads(message)
        table = message['table'] if 'table' in message else None

        if table == 'funding':
            print ("funding")
            self.on_funding_message(message)
        elif table == 'orderBookL2':
            self.on_order_book_message(message)
        elif table == 'trade':
            self.on_trade_message(message)
        return table


    def on_trade_message(self, message):
        for data in message['data']:
            time = time_sec(data['timestamp'])

            price = data['price']
            size = data['size']
            side = data['side']

            if self.trade_time and self.trade_time != time:

                self.trade_tick(self.trade_time, self.trade_buy, self.trade_sell)

                self.trade_buy = {}
                self.trade_sell = {}

            if side == "Buy":
                if price in self.trade_buy:
                    self.trade_buy[price] += size
                else:
                    self.trade_buy[price] = size

            elif side == "Sell":
                if price in self.trade_sell:
                    self.trade_sell[price] += size
                else:
                    self.trade_sell[price] = size
            else:
                print("Error")

            self.trade_time = time


    def on_funding_message(self, message):
        data = message['data'][0]

        time = time_sec(data['timestamp'])
        funding_rate = data['fundingRate']

        if self.funding_tick:
            self.funding_tick(time, funding_rate)

    def on_order_book_message(self, message):
        action = message['action'] if 'action' in message else None
        self.time_stamp = message['TIME'] if 'TIME' in message else None

        if not action:
            return

        if action == 'partial':
            logger.debug('partial')
            self.ready = True
            self.data_hash = {}
            for d in message['data']:
                self.data_hash[d['id']] = d
        elif action == 'insert' and self.ready:
            for d in message['data']:
                self.data_hash[d['id']] = d
        elif action == 'update' and self.ready:
            for d in message['data']:
                for key in d:
                    self.data_hash[d['id']][key] = d[key]
        elif action == 'delete' and self.ready:
            # Locate the item in the collection and remove it.
            for deleteData in message['data']:
                del (self.data_hash[deleteData['id']])
        else:
            logger.debug('wait for partial')
            pass

    def get_market_depth(self):
        return list(self.data_hash.values())

    def load_line(self, line):
        table = self.on_message(line)

        if table == 'orderBookL2':
            order_book = self.get_market_depth()
            if self.order_book_tick and self.ready:
                self.order_book_tick(self.time_stamp, order_book)
        elif table == 'trade':
            if self.trade_tick:
                pass
        elif table == 'funding':
            if self.funding_tick:
                pass

    def _is_gzipfile(self, filename):
        if filename.endswith('.gz'):
            return True
        else:
            return False

    def load(self, file_name):
        print("loading", file_name)

        if self._is_gzipfile(file_name):
            with gzip.open(file_name, "rt") as file:
                for line in file:
                    line = log.encoder.decode(line)
                    self.load_line(line)
        else:
            with open(file_name, "r") as file:
                for line in file:
                    line = log.encoder.decode(line)
                    self.load_line(line)
