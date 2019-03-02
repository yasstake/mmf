import json
import logging

import log.encoder
from log.timeutil import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def findItemByKeys(table, matchData):
    try:
        for item in table:
            if item['id'] == matchData['id']:
                return item
    except:
        logger.debug("findItemByKeys Error")
        logger.debug(item)
        logger.debug(matchData)
    finally:
        pass

    logger.debug("Item not found")
    return None


class LogLoader:
    def __init__(self, order_book_tick = None, trade_tick = None, funding_tick = None):
        self.order_book_tick = order_book_tick
        self.trade_tick = trade_tick
        self.funding_tick = funding_tick

        # order book
        self.data = {}
        self.keys = {}
        self.time_stamp = 0
        self.ready = False

        # funding
        self.funding_time = None
        self.funding_rate = None

        #trade infomation
        self.trade_time = None
        self.trade_sell = {}
        self.trade_buy  = {}

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

            print("--trade->"+ date_string(time) + '/' + str(time) + " " + str(price) + " " + str(size) + " " + side)

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
            self.data = message['data']
        elif action == 'insert' and self.ready:
            logger.debug('insert')
            self.data += message['data']
            pass
        elif action == 'update' and self.ready:
            for updateData in message['data']:
                item = findItemByKeys(self.data, updateData)
                if not item:
                    return  # No item found to update. Could happen before push
                item.update(updateData)
            pass
        elif action == 'delete' and self.ready:
            logger.debug('delete')

            # Locate the item in the collection and remove it.
            for deleteData in message['data']:
                item = findItemByKeys(self.data, deleteData)
                if not item:
                    return
                self.data.remove(item)
            pass
        else:
            logger.debug('wait for partial')
            pass

    def get_market_depth(self):
        return self.data

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

    def load(self, file_name):
        with open(file_name, "r") as file:
            for line in file:
                line = log.encoder.decode(line)
                self.load_line(line)
