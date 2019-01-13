
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

        cursor.execute(
            '''
            create table if not exists sell_trade
                    (time integer,
                     price real,
                     volume integer,
                     primary key(time, price)
                    ) 
            ''')

        cursor.execute(
            '''
            create table if not exists buy_trade
                    (time integer,
                     price real,
                     volume integer,
                     primary key(time, price)
                    ) 
            ''')

        cursor.execute(
            '''
            create table if not exists funding
                    (time integer primary key, 
                     funding real
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

    def insert_order_book(self, time, message):
        sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list = self.message_to_list(message)

        sell_blob = sqlite3.Binary(self.list_to_zip_string(sell_list))
        buy_blob = sqlite3.Binary(self.list_to_zip_string(buy_list))

        sql = 'INSERT or REPLACE into order_book (time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list) values(?, ?, ?, ?, ?, ?, ?)'
        cursor = self.connection.cursor()
        cursor.execute(sql, [time, sell_min, sell_vol, sell_blob, buy_max, buy_vol, buy_blob])
        self.connection.commit()

    def insert_sell_trade(self, time, price, size):
        sql = 'INSERT or REPLACE into sell_trade (time, price, volume) values(?, ?, ?)'
        cursor = self.connection.cursor()
        cursor.execute(sql, [time, price, size])
        self.connection.commit()


    def insert_buy_trade(self, time, price, size):
        sql = 'INSERT or REPLACE into buy_trade (time, price, volume) values(?, ?, ?)'
        cursor = self.connection.cursor()
        cursor.execute(sql, [time, price, size])
        self.connection.commit()


    def insert_funding(self, time, funding):
        sql = 'INSERT or REPLACE into funding (time, funding) values(?, ?)'
        cursor = self.connection.cursor()
        cursor.execute(sql, [time, funding])
        self.connection.commit()

