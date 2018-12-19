
import sys
import os
import glob
import sqlite3
import log.bitws
import zlib


DB_NAME = ":memory:"


class LogDb:
    def __init__(self, db_name = DB_NAME):
        self.db_name = db_name
        self.connection = None
        self.last_time = 0

        pass

    def __del__(self):
        self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)

    def create(self):
        '''create db'''
        cursor = self.connection.cursor()

        cursor.execute(
            '''
            create table if not exists order_book
                    (time integer primary key, 
                    sell_min integer, sell_vol integer, sell_list BLOB,
                    buy_max  integer, buy_vol  integer, buy_list BLOB
                    ) 
            ''')

        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def message_to_list(self, message):
        sell_min = 999999999
        sell = {}
        sell_vol = 0

        buy_max = 0
        buy = {}
        buy_vol = 0

        for item in message:
            volume = item['size']
            price = item['price']

            if (item['side'] == 'Sell'):
                side = 0
                sell[price] = volume
                if price < sell_min:
                    sell_min = price
                if sell_vol < volume:
                    sell_vol = volume
            else:
                side = 1
                buy[price] = volume
                if buy_max < price:
                    buy_max = price

                if buy_vol < volume:
                    buy_vol = volume

        buy_list = []
        for i in range(256):
            index = buy_max - i * 0.5
            if index in buy:
                buy_list.append(buy[index])
            else:
                break

        sell_list = []
        for i in range(256):
            index = sell_min + i * 0.5
            if index in sell:
                sell_list.append(sell[index])
            else:
                break

        return sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list

    def list_to_zip_string(self, message_list):
        message_string = ''
        for m in message_list:
            message_string += str(m)
            message_string += ','

        return zlib.compress(message_string[:-1].encode())


    def zip_string_to_list(self, zip_string):
        message_string = zlib.decompress(zip_string)
        message_array =  message_string.decode().split(',')

        message = []
        for m in message_array:
            message.append(int(m))

        return message

    def insert(self, time, message):
        sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list = self.message_to_list(message)

        sell_blob = sqlite3.Binary(self.list_to_zip_string(sell_list))
        buy_blob = sqlite3.Binary(self.list_to_zip_string(buy_list))

        sql = 'INSERT or REPLACE into order_book (time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list) values(?, ?, ?, ?, ?, ?, ?)'
        cursor = self.connection.cursor()
        cursor.execute(sql, [time, sell_min, sell_vol, sell_blob, buy_max, buy_vol, buy_blob])
        self.connection.commit()

    def tick(self, time_stamp, order_book):
        if self.last_time != time_stamp:
            self.insert(time_stamp, order_book)
        self.last_time = time_stamp

    def load_file(self, file):
        log_loader = log.bitws.LogLoader()
        log_loader.load(self.tick, file)


if __name__ == '__main__':
    log_dir = '/tmp'
    db_file = '/tmp/bitlog.db'

    if len(sys.argv) == 2:
        log_dir = sys.argv[0]
        db_file = sys.argv[1]

    print (log_dir, db_file)

    log_db = LogDb(db_file)
    log_db.connect()
    log_db.create()

    log_files = glob.glob(log_dir + '/' + '*.log')

    for file in log_files:
        print (file)
        log_db.load_file(file)

    log_db.close()

