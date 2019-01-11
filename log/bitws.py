import datetime
import json
import os
import traceback
from bitmex_websocket import BitMEXWebsocket

# needs install
import websocket

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

try:
    import thread
except ImportError:
    import _thread as thread
import time


def encode(message):
    message = message.replace(',"price":', ',p:')
    message = message.replace(',"size":', ',s:')
    message = message.replace('"id":', 'i:')
    message = message.replace('"side"', '"S"')
    message = message.replace('"types"', '"T"')
    message = message.replace('"table"', '"t"')
    message = message.replace('"Sell"', '"H"')
    message = message.replace('"Buy"', '"L"')
    message = message.replace('"orderBookL2"', '"O"')
    message = message.replace('"action"', '"A"')
    message = message.replace('"update"', '"U"')
    message = message.replace('"data"', '"d"')
    return message


def decode(message):
    message = message.replace(',p:', ',"price":')
    message = message.replace(',s:', ',"size":')
    message = message.replace('i:', '"id":')
    message = message.replace('"S"', '"side"')
    message = message.replace('"T"', '"types"')
    message = message.replace('"t"', '"table"')
    message = message.replace('"H"', '"Sell"')
    message = message.replace('"L"', '"Buy"')
    message = message.replace('"O"', '"orderBookL2"')
    message = message.replace('"A"', '"action"')
    message = message.replace('"U"', '"update"')
    message = message.replace('"d"', '"data"')

    return message


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
    def __init__(self):
        self.data = {}
        self.keys = {}
        self.time_stamp = 0
        self.ready = False

    def on_message(self, message):
        message = json.loads(message)
        table = message['table'] if 'table' in message else None

        if table == 'funding':
            print ("funding")
            self.on_funding_message(message)
        elif table == 'orderBookL2':
            self.on_order_book_message(message)
        elif table == 'trade':
            logger.debug("--trade--")
            self.on_trade_message(message)
        return table


    def on_trade_message(self, message):
        action = message['action'] if 'action' in message else None
        self.time_stamp = message['TIME'] if 'TIME' in message else None


    def on_funding_message(self, message):
        action = message['action'] if 'action' in message else None
        self.time_stamp = message['TIME'] if 'TIME' in message else None

        if action == 'partial':
            data = message['data'][0]

            timestamp = data['timestamp']
            funding_rate = data['fundingRate']

            print(timestamp)
            print(funding_rate)
            pass

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

    def load(self, tick, file_name):

        with open(file_name, "r") as file:
            for line in file:
                line = decode(line)

                table = self.on_message(line)

                if table == 'orderBookL2':
                    order_book = self.get_market_depth()
                    if tick and self.ready:
                        tick(self.time_stamp, order_book)
        pass


class BitWs:
    '''logging utility using bitmex realtime(websockets) API'''

    def __init__(self, log_file_dir="/tmp"):
        self.last_action = None
        self.log_file_root_name = None
        self.log_file_name = None
        self.ws = None
        self.log_file_dir = log_file_dir

        self.reset()
        self.rotate_file()

    def __del__(self):
        # self.dump_message()
        self.rotate_file()
        self.remove_terminate_flag()

    def reset(self):
        self.last_message = None
        self.reset_timestamp()

    def get_flag_file_name(self):
        return "/tmp/BITWS-FLG"

    def create_terminate_flag(self):
        self.remove_terminate_flag()
        file_name = self.get_flag_file_name()
        with open(file_name + "tmp", "w") as file:
            file.write(str(os.getpid()))
            file.close()
            os.rename(file_name + "tmp", file_name)

    def check_terminate_flag(self):
        file_name = self.get_flag_file_name()

        if os.path.isfile(file_name):
            with open(file_name, "r") as file:
                id = file.readline()
                if id != str(os.getpid()):
                    return True
        return False

    def remove_terminate_flag(self):
        file_name = self.get_flag_file_name()
        if os.path.isfile(file_name):
            os.remove(file_name)

    def timestamp(self):
        now = datetime.datetime.utcnow()
        return int(now.timestamp())

    def reset_timestamp(self):
        self.last_time = self.timestamp()

    def date_string(self):
        time = datetime.datetime.fromtimestamp(self.timestamp())

        return time.strftime('%Y-%m-%d')

    def time_stamp_string(self):
        time = datetime.datetime.fromtimestamp(self.timestamp())
        return time.isoformat()

    #        return time.strftime('%Y-%m-%d-%H:%M:%S')

    def rotate_file(self):
        if self.log_file_name:
            if os.path.isfile(self.log_file_name):
                os.rename(self.log_file_name, self.log_file_root_name)

        self.log_file_root_name = self.log_file_dir + '/' + self.time_stamp_string() + ".log"
        self.log_file_name = self.log_file_root_name + ".current"

    def dump_message(self):
        if self.last_message is None:
            return
        self.dump_message_line(self.last_message)
        self.reset()

    def dump_message_line(self, message):
        message['TIME'] = self.last_time
        with open(self.log_file_name, "a") as file:
            json_string = json.dumps(message, separators=(',', ':'))
            file.write(encode(json_string))
            file.write('\n')

    def remove_symbol(self, message):
        for m in message['data']:
            del (m['symbol'])

    def on_message(self, ws, message):
        message = json.loads(message)
        table = message['table'] if 'table' in message else None


        if table == "orderBookL2":
            self.remove_symbol(message)
            self.on_order_book_message(ws, message)
        elif table == "funding":
            self.remove_symbol(message)
            self.on_funding_message(ws, message)
        elif table == "trade":
            self.remove_symbol(message)
            self.on_trade_message(ws, message)

    def on_trade_message(self, ws, message):
        logger.debug("trade")
        self.dump_message_line(self.strip_trade_message(message))


    def strip_trade_message(self, message):
        data = message['data']
        side = None
        price = 0
        size = 0

        last_time_stamp = data[0]['timestamp']
        for d in data:
            if last_time_stamp != d['timestamp']:
                break

            side =  d['side']
            price = d['price']
            size += d['size']

        del(data[1:])

        data[0]['side'] = side
        data[0]['price'] = price
        data[0]['size'] = size
        del(data[0]['grossValue'], data[0]['homeNotional'], data[0]['trdMatchID'], data[0]['foreignNotional'])

        return message


    def on_funding_message(self, ws, message):
        logger.debug("funding")
        self.dump_message_line(message)
        pass

    def on_order_book_message(self, ws, message):
        action = message['action'] if 'action' in message else None

        if action == 'partial':
            logger.debug("partial")
            self.rotate_file()
            self.create_terminate_flag()

        current_time = self.timestamp()

        if current_time == self.last_time and self.last_action == action and action != None:
            if self.last_message != None:
                self.last_message['data'] += message['data']
            else:
                self.last_message = message
        else:
            if self.last_message != None:
                self.dump_message()
            self.last_message = message

        self.reset_timestamp()
        self.last_action = action

        if self.check_terminate_flag():
            self.ws.close()
            logger.debug("terminated")

    def on_error(self, ws, error):
        logger.debug(error)

    def on_close(self, ws):
        logger.debug("### closed ###")

    def on_open(self, ws):
        ws.send('{"op": "subscribe", "args": ["funding:XBTUSD", "orderBookL2:XBTUSD", "trade:XBTUSD"]}')

    def start(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://www.bitmex.com/realtime",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)

        self.ws.run_forever(ping_interval=70, ping_timeout=10)

    def load_log(self, file_name):
        pass


if __name__ == "__main__":
    bitmex = BitWs()
    bitmex.start()
