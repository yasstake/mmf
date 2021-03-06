import atexit
import json
import logging
import os

# needs install
import websocket

from log.timeutil import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

import log.encoder

try:
    import thread
except ImportError:
    import _thread as thread


class BitWs:
    '''logging utility using bitmex realtime(websockets) API'''

    def __init__(self, log_file_dir=os.sep + "tmp", flag_file_name = os.sep + "tmp" + os.sep + "BITWS-FLG", id = None, fix_file=None):
        self.last_action = None
        self.log_file_root_name = None
        self.log_file_name = None
        self.ws = None
        self.log_file_dir = log_file_dir
        self.last_time = 0
        self.compress = True
        self.terminate_count = 200
        self.terminated_by_peer = False
        self.fix_file = fix_file
        if id:
            self.pid = id
        else:
            self.pid = str(os.getpid())

        self.reset()

        self.flag_file_name = flag_file_name

        if not self.fix_file:
            self.rotate_file()

    def __del__(self):
        # self.dump_message()
        self.rotate_file()
        self.remove_terminate_flag()

    def reset(self):
        self.last_message = None
        self.reset_timestamp()

    def reset_timestamp(self):
        self.last_time = int(timestamp())

    def get_flag_file_name(self):
        return self.flag_file_name

    def create_terminate_flag(self):
        self.remove_terminate_flag()
        file_name = self.get_flag_file_name()
        with open(file_name + "tmp", "w") as file:
            file.write(self.get_process_id())
            file.close()
            os.rename(file_name + "tmp", file_name)

    def check_terminate_flag(self):
        file_name = self.get_flag_file_name()

        if os.path.isfile(file_name):
            with open(file_name, "r") as file:
                id = file.readline()
                if id != self.get_process_id():
                    self.terminate_count = self.terminate_count - 1
                    if self.terminate_count == 0:
                        return True
        return False

    def get_process_id(self):
        return self.pid

    def remove_terminate_flag(self):
        file_name = self.get_flag_file_name()
        if os.path.isfile(file_name):
            os.remove(file_name)

    def rotate_file(self):
        if self.log_file_name:
            if os.path.isfile(self.log_file_name):
                os.rename(self.log_file_name, self.log_file_root_name)

        timestring = time_stamp_string().replace(":", "-").replace('+', '-')

        self.log_file_root_name = self.log_file_dir + os.sep + 'BITLOG' + self.get_process_id() + '-' + timestring + ".log"

        self.log_file_name = self.log_file_root_name + ".current"


    def dump_message(self):
        if self.last_message is None:
            return
        self.dump_message_line(self.last_message)
        self.reset()

    def dump_message_line(self, message):
        message['TIME'] = self.last_time

        if self.fix_file:
            file_name = self.fix_file
        else:
            file_name = self.log_file_name

        with open(file_name, "a") as file:
            json_string = json.dumps(message, separators=(',', ':'))

            if self.compress:
                file.write(log.encoder.encode(json_string))
            else:
                file.write(json_string)
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
#        logger.debug("trade")
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

        current_time = int(timestamp())

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
            self.rotate_file()
            self.terminated_by_peer = True
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

        self.ws.run_forever(ping_interval=70, ping_timeout=30)


if __name__ == "__main__":
    bitmex = BitWs(fix_file='/tmp/bit.log')
    atexit.register(bitmex.rotate_file)
    bitmex.start()


