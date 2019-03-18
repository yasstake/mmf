
import sys
import os
import glob
import sqlite3
import log.bitws
import zlib
from log import constant

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
        cursor = self.connection.cursor()
        self._create_db(cursor)

    def _create_db(self, cursor):
        '''create db'''

        cursor.execute(
            '''
            create table if not exists order_book
                    (time integer primary key, 
                    sell_min integer, sell_volume integer, sell_list BLOB,
                    buy_max  integer, buy_volume  integer, buy_list BLOB,
                    market_order_sell integer default NULL,
                    market_order_buy integer default NULL,
                    fix_order_sell integer default NULL,
                    fix_order_buy integer default NULL
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
                    sell_vol = volume
            else:
                side = 1
                buy[price] = volume
                if buy_max < price:
                    buy_max = price
                    buy_vol = volume

        buy_list = []
        for i in range(constant.BOOK_DEPTH):
            index = buy_max - i * constant.PRICE_UNIT
            if index in buy:
                buy_list.append(buy[index])
            else:
                break

        sell_list = []
        for i in range(constant.BOOK_DEPTH):
            index = sell_min + i * constant.PRICE_UNIT
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

    def insert_order_book_message(self, time, message):
        sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list = self.message_to_list(message)
        self.insert_order_book(time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list)

    def insert_order_book(self, time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list):
        sell_blob = sqlite3.Binary(self.list_to_zip_string(sell_list))
        buy_blob = sqlite3.Binary(self.list_to_zip_string(buy_list))

        sql = 'INSERT or REPLACE into order_book (time, sell_min, sell_volume, sell_list, buy_max, buy_volume, buy_list) values(?, ?, ?, ?, ?, ?, ?)'
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

    def calc_center_price(self, min, max):
        diff = max - min
        if diff == constant.PRICE_UNIT:
            return max
        else:
            return min + (int((diff + constant.PRICE_UNIT)))/2

    def select_board_price(self, time):
        """
        :param time:
        :return: time, center_price
        """
        sql = "select sell_min, buy_max from order_book where time = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, (time,))

        prices = cursor.fetchone()

        if prices:
            return prices
        else:
            return None

    def select_center_price(self, time):
        prices = self.select_board_price(time)

        if prices:
            sell_min, buy_max = prices
            return self.calc_center_price(buy_max, sell_min)
        else:
            return None


    def select_order_book(self, time):
        """
        :param time:
        :return: time, sell_list, buy_list
        """
        sql = "select time, sell_min, sell_list, buy_max, buy_list from order_book where time = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, (time,))

        rec = cursor.fetchone()

        if not rec:
            return None

        time, sell_min, sell_list, buy_max, buy_list = rec

        return time, sell_min, self.zip_string_to_list(sell_list), buy_max, self.zip_string_to_list(buy_list)


    def select_sell_trade(self, time, window = 1):
        """
        :param time:
        :return: sell_trade_list
        """
        sql = "select time, price, volume from sell_trade where ? < time and time <= ? order by price"
        cursor = self.connection.cursor()

        return cursor.execute(sql,(time - window, time)).fetchall()

    def select_buy_trade(self, time, window = 1):
        """
        :param time:
        :return: buy_trade list
        """
        sql = "select time, price, volume from buy_trade where ? < time and time <= ? order by price desc"
        cursor = self.connection.cursor()

        return cursor.execute(sql,(time - window, time)).fetchall()

    def select_funding(self, time):
        """
        :param time:
        :return: time_to_remain, funding_rate
        """
        sql = "select time, funding from funding where time <= ? order by time"
        cursor = self.connection.cursor()

        rec = cursor.execute(sql, (time,)).fetchone()

        if not rec:
            return None

        t, funding = rec
        ttr = time - t

        if ttr <= 8 * 60 * 60:
            return ttr, funding

        return None

    def select_order_book_price(self, time):
        """
        :return: sell_min, sell_volume, buy_max, buy_volume
        """
        sql_select_sell_price = "select sell_min, sell_volume, buy_max, buy_volume from order_book where time = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql_select_sell_price, (time,))

        return cursor.fetchone()

    def select_order_book_price_with_retry(self, time, retry = 30):
        rec = None

        while retry != 0 and rec is None:
            rec = self.select_order_book_price(time)
            time = time + 1

        return rec


    def calc_market_order_buy(self, time, order_volume):
        """
        calc market buy price
        basically the price will be the top edge of the order book if there is enough volume on the board.
        if there is not enough volume, the price will be slip two tick.
        :return: the target price. return None: if not found the data.
        """
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec

        if order_volume * 2 < sell_volume: # 2 means enough margin
            return sell_min
        else:
            return sell_min + constant.PRICE_UNIT * 2


    def calc_market_order_sell(self, time, order_volume):
        """
        calc market buy price
        basically the price will be the bottom edge of the order book if there is enough volume on the board.
        if there is not enough volume, the price will be slip two tick.
        :return: the target price. return None: if not found the data.
        """
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec

        if order_volume * 2 < buy_volume: # 2 means enough margin
            return buy_max
        else:
            return buy_max - constant.PRICE_UNIT * 2


    def is_suceess_fixed_order_sell(self, time, price, volume, time_width = 600):

        sql_count_sell_trade  = 'select sum(volume) from buy_trade where  ? <= time and time < ? and ? <= price'

        cursor = self.connection.cursor()
        cursor.execute(sql_count_sell_trade, (time, time + time_width, price))

        amount = cursor.fetchone()


        if amount[0] is None:
            return False

        if volume * 2 < amount[0]: # 2 is enough margin
            return True
        else:
            return False

    def _calc_order_book_price_sell(self, time):
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec
        return sell_min

    def calc_fixed_order_sell(self, time, volume, time_width=600):
        """

        :param time: unix time at the order
        :param price: order price
        :param volume: order volume
        :param time_width: wait to order (sec)
        :return: price to be executed nor None if not excuted.
        """
        price = self._calc_order_book_price_sell(time)

        if self.is_suceess_fixed_order_sell(time, price, volume):
            return price
        else:
            return None


    def is_suceess_fixed_order_buy(self, time, price, volume, time_width = 600):
        sql_count_sell_trade  = 'select sum(volume) from sell_trade where  ? <= time and time < ? and price <= ?'

        cursor = self.connection.cursor()
        cursor.execute(sql_count_sell_trade, (time, time + time_width, price))

        amount = cursor.fetchone()

        if amount[0] is None:
            return False

        if volume * 2 < amount[0]: # 2 is enough margin
            return True
        else:
            return False

    def _calc_order_book_price_buy(self, time):
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec
        return buy_max

    def calc_fixed_order_buy(self, time, volume, time_width = 600):
        """

        :param time: time in unix time
        :param volume: order volume
        :param time_width: time to execute
        :return: expected price or None if not executed.
        """
        sell_min = self._calc_order_book_price_buy(time)

        if self.is_suceess_fixed_order_buy(time, sell_min, volume):
            return sell_min
        else:
            return None

    def update_all_order_prices(self):

        time_sql = """select time from order_book where market_order_sell is NULL"""
        update_sql = """update order_book set market_order_sell = ?, market_order_buy = ?, fix_order_sell = ?, fix_order_buy = ? where time = ?"""

        cursor = self.connection.cursor()
        cursor.execute(time_sql)

        if not cursor:
            return None

        records = cursor.fetchall()

        for rec in records:
            time = rec[0]
            market_order_sell = self.calc_market_order_sell(time, 1)
            print(market_order_sell)
            market_order_buy  = self.calc_market_order_buy(time, 1)
            fix_order_sell = self.calc_fixed_order_sell(time, 1)
            fix_order_buy  = self.calc_fixed_order_buy(time, 1)

            cursor.execute(update_sql, (market_order_sell, market_order_buy, fix_order_sell, fix_order_buy, time))
            self.connection.commit()


    def calc_latest_time(self):
        time_sql = """select time from order_book order by time desc"""

        cursor = self.connection.cursor()
        cursor.execute(time_sql)

        if not cursor:
            return None

        records = cursor.fetchone()

        return records[0]

    def dump_db(self, file='/tmp/bitlog.dump'):
        dump_sql = '''select * from order_book order by time'''

        cursor = self.connection.cursor()
        cursor.execute(dump_sql)

        with open(file, "w") as f:
            for line in cursor.fetchall():
                f.write(line)
                f.write('\n')

    def copy_db(self, source, destination, start_time=0, duration=0):
        conn = sqlite3.connect(destination)

        cu = conn.cursor()
        self._create_db(cu)

        cu.execute("attach database '" + source + "'as source_db")

        self._create_db(cu)

#        sql = "insert into order_book select * from source_db.order_book where " + str(start_time) + " <= time and time < " + str(start_time + duration)
        sql = "insert or replace into order_book select * from source_db.order_book where {0} <= time and time < {1}".format(str(start_time), str(start_time+duration))
        print(sql)
        cu.execute(sql)
        conn.commit()

        sql = "insert or replace into sell_trade select * from source_db.sell_trade where {0} <= time and time < {1}".format(str(start_time), str(start_time+duration))
        print(sql)
        cu.execute(sql)
        conn.commit()


        sql = "insert or replace into buy_trade select * from source_db.buy_trade where {0} <= time and time < {1}".format(str(start_time), str(start_time+duration))
        print(sql)
        cu.execute(sql)
        conn.commit()

        sql = "insert or replace into funding select * from source_db.funding where {0} <= time and time < {1}".format(str(start_time), str(start_time+duration))
        print(sql)
        cu.execute(sql)
        conn.commit()

        cu.execute("detach database source_db")




        destination = sqlite3.connect(destination)




    def import_db(self, file='/tmp/bitlog.dump'):
        with open(file) as f:
            for line in f:
                self.connection.executescript(line)
                print(line)



