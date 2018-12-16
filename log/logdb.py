
import sys
import os
import sqlite3


DB_NAME = ":memory:"


class LogDb:
    def __init__(self, db_name = DB_NAME):
        self.db_name = db_name
        self.connection = None
        pass

    def __del__(self):
        self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)

    def create(self):
        '''create db'''
        cursor = self.connection.cursor()

        cursor.execute('''create table order_book (time integer, side integer, price real, size real) ''')
        cursor.execute(
            '''create table order_book_info
                    (time integer, sell_min real, sell_max real, sell_max_vol real, 
                     buy_min real, buy_max real, buy_max_vol real) ''')

        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def insert(self, time, message):
        print(time)

        cursor = self.connection.cursor()

        sell_min = 99999999
        sell_max = 0
        sell_max_vol = 0

        buy_min = 99999999
        buy_max = 0
        buy_max_vol = 0

        for item in message:
            volume = item['size']
            price = item['price']

            if(item['side'] == 'Sell'):
                side = 0
                if (sell_max < price):
                    sell_max = price
                if (price < sell_min):
                    sell_min = price
                if (sell_max_vol):
                    sell_max_vol = volume
            else:
                side = 1
                if(buy_max < price ):
                    buy_max = price
                if(price < buy_min):
                    buy_min = price
                if(sell_max_vol):
                    buy_max_vol = volume

            cursor.execute('INSERT or replace into order_book values(?,?,?,?)', [time, side, item['size'], item['price']])

            cursor.execute('INSERT or replace into order_book_info values(?,?,?,?,?,?,?)',
                            [time, sell_min, sell_max, sell_max_vol, buy_min, buy_max, buy_max_vol])

            print(item)
            print (time, side, item['size'], item['price'])




        self.connection.commit()



