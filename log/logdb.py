import sqlite3
import zlib
from functools import lru_cache
import numpy as np
from log.constant import *
from log.loader import LogLoader
from log.qvalue import HOLD_TIME_MAX
from log.qvalue import QValue
from log.qvalue import OrderPrices
from log.qvalue import Q_DISCOUNT_RATE
from log.qvalue import Q_FIRST_DISCOUNT_RATE
from log.qvalue import HOLD_TIME_MAX
from log.qvalue import EXECUTE_TIME_MIN


DB_NAME = ":memory:"

ORDER_TIME_WIDTH = 120


class LogDb:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.connection = None
        self.last_time = 0
        self.cursor = None

    def __del__(self):
        # self.close()
        # todo: ensure db file is closed
        pass

    def connect(self):
        if self.db_name:
            print("open db name=", self.db_name)
            self.connection = sqlite3.connect(self.db_name)
        else:
            print('Inmemory db created')
            self.connection = sqlite3.connect(DB_NAME, uri=True)

    def create_cursor(self):
        if self.cursor:
            self.commit()

        self.cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.commit()

            self.connection.close()
            self.connection = None

    def commit(self):
        if self.connection:
            self.connection.commit()

    def create(self):
        self._create_table(self.cursor)

    def _create_table(self, cursor):
        '''create db'''

        cursor.execute(
            '''
            create table if not exists order_book
                    (time integer primary key, 
                    sell_min integer, sell_volume integer, sell_list BLOB,
                    buy_max  integer, buy_volume  integer, buy_list BLOB,
                    ba integer default NULL,
                    market_order_sell integer default NULL,
                    market_order_buy integer default NULL,
                    fix_order_sell integer default NULL,
                    fix_order_sell_time integer default NULL,                    
                    fix_order_buy integer default NULL,
                    fix_order_buy_time integer default NULL
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

        cursor.execute(
            '''
            create table if not exists q
                  (
                      time integer, 
                      start_time integer, 
                      start_action integer,
                      nop_q real,
                      buy_q real,
                      buy_now_q real,
                      sell_q real,
                      sell_now_q real,
                      primary key(time, start_time, start_action)
                  )
            '''
        )

        cursor.execute(
            '''
            create index if not exists q_start_time_index on q (start_time) 
            '''
        )


    def list_to_zip_string(self, message_list):
        return self.list_to_bin(message_list)

    def _list_to_zip_string(self, message_list):
        message_string = ''
        for m in message_list:
            message_string += str(m)
            message_string += ','

        return zlib.compress(message_string[:-1].encode())

    def list_to_bin(self, message_list):
        message_array = np.array(message_list, dtype=np.float32)
        data = message_array.data
        #return data
        return zlib.compress(data)

    def zip_string_to_list(self, zip_string):
        return self.bin_to_list(zip_string)

    def _zip_string_to_list(self, zip_string):
        message_array = zlib.decompress(zip_string).decode().split(',')
        return list(map(int, message_array))

    def bin_to_list(self, zip_bin):
        bin_message = zlib.decompress(zip_bin)

        list = np.frombuffer(bin_message, dtype=np.float32)

        # todo debug
        return list

    def insert_order_book_message(self, time, message):
        sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list = LogLoader.message_to_list(message)
        self.insert_order_book(time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list)

    def insert_order_book(self, time, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list):
        if len(sell_list) < 10  or  len(buy_list) < 10:
            print("TOOSHORT->", time, buy_list, sell_list)

        sell_blob = sqlite3.Binary(self.list_to_zip_string(sell_list))
        buy_blob = sqlite3.Binary(self.list_to_zip_string(buy_list))

        sql = 'INSERT or REPLACE into order_book (time, sell_min, sell_volume, sell_list, buy_max, buy_volume, buy_list) values(?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(sql, [time, sell_min, sell_vol, sell_blob, buy_max, buy_vol, buy_blob])

    def insert_sell_trade(self, time, price, size):
        sql = 'INSERT or REPLACE into sell_trade (time, price, volume) values(?, ?, ?)'
        self.cursor.execute(sql, [time, price, size])

    def insert_buy_trade(self, time, price, size):
        sql = 'INSERT or REPLACE into buy_trade (time, price, volume) values(?, ?, ?)'
        self.cursor.execute(sql, [time, price, size])

    def insert_funding(self, time, funding):
        sql = 'INSERT or REPLACE into funding (time, funding) values(?, ?)'
        self.cursor.execute(sql, [time, funding])

    def calc_center_price(self, min_price, max_price):
        diff = max_price - min_price
        if diff == PRICE_UNIT:
            return max_price
        else:
            return min_price + (int((diff + PRICE_UNIT))) / 2

    def select_book_price(self, time):
        """
        :param time:
        :return: time, center_price
        """
        sql = "select sell_min, sell_volume, buy_max, buy_volume from order_book where time = ?"

        self.cursor.execute(sql, (time,))

        prices = self.cursor.fetchone()

        if prices:
            return prices
        else:
            return None

    def select_center_price(self, time):
        prices = self.select_book_price(time)

        if prices:
            sell_min, sell_vol, buy_max, buy_vol = prices
            return self.calc_center_price(buy_max, sell_min)
        else:
            return None

    @lru_cache(maxsize=2048)
    def select_order_book(self, time):
        """
        :param time:
        :return: time, sell_list, buy_list
        """
        sql = "select time, sell_min, sell_list, buy_max, buy_list from order_book where time = ?"
        self.cursor.execute(sql, (time,))

        rec = self.cursor.fetchone()

        if not rec:
            return None

        time, sell_min, sell_list, buy_max, buy_list = rec

        if len(sell_list) < 30:
            print('-----short--indb>', time, self.zip_string_to_list(sell_list))

        return time, sell_min, self.zip_string_to_list(sell_list), buy_max, self.zip_string_to_list(buy_list)

    @lru_cache(maxsize=2048)
    def select_sell_trade(self, time, window = 1):
        """
        :param time:
        :return: sell_trade_list
        """
        sql = "select price, volume from sell_trade where ? < time and time <= ? order by price"

        return self.cursor.execute(sql,(time - window, time)).fetchall()

    @lru_cache(maxsize=2048)
    def select_buy_trade(self, time, window = 1):
        """
        :param time:
        :return: buy_trade list
        """
        sql = "select price, volume from buy_trade where ? < time and time <= ? order by price desc"

        return self.cursor.execute(sql,(time - window, time)).fetchall()

    def select_funding(self, time):
        """
        :param time:
        :return: time_to_remain, funding_rate
        """
        sql = "select time, funding from funding where time <= ? order by time"

        rec = self.cursor.execute(sql, (time,)).fetchone()

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

        self.cursor.execute(sql_select_sell_price, (time,))

        return self.cursor.fetchone()

    @lru_cache(maxsize=2048)
    def select_order_book_price_with_retry(self, time, retry=30):
        rec = None

        while retry != 0 and rec is None:
            rec = self.select_order_book_price(time)
            time = time + 1

        return rec

    def select_expected_price(self, time):
        sql = """select market_order_sell, market_order_buy, fix_order_sell, fix_order_buy from order_book where time = ?"""

        self.cursor.execute(sql, (time,))
        return self.cursor.fetchone()

    def select_expected_price_with_time(self, time):
        '''
        select one record from order price info with time
        :param time:
        :return:
        '''
        sql = """select market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time, fix_order_buy, fix_order_buy_time from order_book where time = ?"""

        self.cursor.execute(sql, (time,))
        return self.cursor.fetchone()


    def select_best_action(self, time):
        sql = """select ba from order_book where time = ?"""

        self.cursor.execute(sql, (time,))

        ba = self.cursor.fetchone()

        if ba:
            return ba[0]
        else:
            return None

    def calc_best_actions(self, time):
        best_action = self.select_best_action(time)

        return self._calc_best_actions(best_action)

    def _calc_best_actions(self, best_action):
        ba_nop = 0
        ba_buy = 0
        ba_buy_now = 0
        ba_sell = 0
        ba_sell_now = 0

        if best_action == ACTION.NOP or best_action is None:
            ba_nop = 1
        elif best_action == ACTION.SELL:
            ba_sell = 1
        elif best_action == ACTION.SELL_NOW:
            ba_sell_now = 1
        elif best_action == ACTION.BUY:
            ba_buy = 1
        elif best_action == ACTION.BUY_NOW:
            ba_buy_now = 1

        return (ba_nop, ba_buy, ba_buy_now, ba_sell, ba_sell_now)

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

        if order_volume * 1.5 < sell_volume: # 1.5 means enough margin
            return sell_min
        else:
            return sell_min + PRICE_UNIT

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

        if order_volume * 1.5 < buy_volume: # 2 means enough margin
            return buy_max
        else:
            return buy_max - PRICE_UNIT

    def is_suceess_fixed_order_sell(self, time, price, volume, time_width = ORDER_TIME_WIDTH):
        sell_min, sell_volume, buy_max, buy_volume = self.select_order_book_price_with_retry(time)

        sql_count_sell_trade = 'select sum(volume) from buy_trade where  ? <= time and time < ? and ? <= price'

        end_time = time + time_width
        self.cursor.execute(sql_count_sell_trade, (time, end_time, price))

        amount = self.cursor.fetchone()

        if amount[0] is None:
            return False

        if volume + sell_volume < amount[0]:
            return price, end_time
        else:
            return False

    def _calc_order_book_price_sell(self, time):
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec
        return sell_min

    MIN_ORDER_TIME = 60

    def calc_fixed_order_sell(self, time, volume, time_width=ORDER_TIME_WIDTH):
        """
        :param time: unix time at the order
        :param price: order price
        :param volume: order volume
        :param time_width: wait to order (sec)
        :return: (price, time) to be executed nor None if not executed
        """
        price = self._calc_order_book_price_sell(time)

        window = LogDb.MIN_ORDER_TIME

        result = None
        while window <= time_width:
            result = self.is_suceess_fixed_order_sell(time, price, volume, window)
            if result:
                break
            window += LogDb.MIN_ORDER_TIME

        return result

    def is_suceess_fixed_order_buy(self, time, price, volume, time_width=ORDER_TIME_WIDTH):
        sell_min, sell_volume, buy_max, buy_volume = self.select_order_book_price_with_retry(time)
        sql_count_sell_trade  = 'select sum(volume) from sell_trade where  ? <= time and time < ? and price <= ?'

        end_time = time + time_width
        self.cursor.execute(sql_count_sell_trade, (time, end_time, price))
        amount = self.cursor.fetchone()

        if amount[0] is None:
            return None

        if volume + buy_volume < amount[0]:
            return price, end_time
        else:
            return None

    def _calc_order_book_price_buy(self, time):
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None

        sell_min, sell_volume, buy_max, buy_volume = rec
        return buy_max

    def calc_fixed_order_buy(self, time, volume, time_width=ORDER_TIME_WIDTH):
        """
        :param time: time in unix time
        :param volume: order volume
        :param time_width: time to execute
        :return: (price, time) to be executed nor None if not executed.
        """
        price = self._calc_order_book_price_buy(time)
        window = LogDb.MIN_ORDER_TIME

        result = None

        while window <= time_width:
            result = self.is_suceess_fixed_order_buy(time, price, volume, window)
            if result:
                break
            window += LogDb.MIN_ORDER_TIME
        
        return result

    def update_all_order_prices(self, force=False):
        if force:
            time_sql = """select time, sell_min from order_book"""
        else:
            time_sql = """select time, sell_min from order_book where market_order_sell is NULL"""

        update_sql = """update order_book set market_order_sell = ?, market_order_buy = ?, fix_order_sell = ?, fix_order_sell_time = ?, fix_order_buy = ?, fix_order_buy_time = ? where time = ?"""

        self.cursor.execute(time_sql)

        for rec in self.cursor.fetchall():
            time, sell_min = rec

            market_order_sell = self.calc_market_order_sell(time, sell_min)
            if market_order_sell is None:
                print("cont")
                continue

            market_order_buy  = self.calc_market_order_buy(time, sell_min)
            if market_order_buy is None:
                continue

            # fix order
            fix_order_sell, fix_order_sell_time = (None, None)
            result = self.calc_fixed_order_sell(time, sell_min)
            if result:
                fix_order_sell, fix_order_sell_time = result

            fix_order_buy, fix_order_buy_time = (None, None)
            result = self.calc_fixed_order_buy(time, sell_min)
            if result:
                fix_order_buy, fix_order_buy_time = result

            if market_order_sell:
                market_order_sell *= TAKER_SELL

            if market_order_buy:
                market_order_buy *= TAKER_BUY

            if fix_order_sell:
                fix_order_sell *= MAKER_SELL

            if fix_order_buy:
                fix_order_buy *= MAKER_BUY

            print(time, 'sell->', market_order_sell, ' buy->', market_order_buy, ' sell(fix)->',
                  fix_order_sell, '(', fix_order_sell_time, ')  buy(fix)->',
                  fix_order_buy, '(', fix_order_buy_time, ')')

            self.cursor.execute(update_sql, (market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time,
                                             fix_order_buy, fix_order_buy_time, time))

    def select_order_prices(self, time):
        select_order_sql = """select market_order_sell, market_order_buy, fix_order_sell, fix_order_buy from order_book where time = ?"""
        self.cursor.execute(select_order_sql, (time,))
        rec = self.cursor.fetchone()
        if rec is None:
            return None
        market_order_sell, market_order_buy, fix_order_sell, fix_order_buy = rec

        return market_order_sell, market_order_buy, fix_order_sell, fix_order_buy

    def select_best_order_prices(self, time, width):
        select_sql = """select max(market_order_sell) from order_book where ? <= time and time <= ?"""
        self.cursor.execute(select_sql, (time, time + width))
        rec = self.cursor.fetchone()
        if rec is None:
            return None
        market_order_sell = rec[0]

        select_sql = """select max(fix_order_sell) from order_book where ? <= time and time <= ?"""
        self.cursor.execute(select_sql, (time,time + width))
        rec = self.cursor.fetchone()
        if rec is None:
            return None
        fix_order_sell = rec[0]

        select_sql = """select min(market_order_buy) from order_book where ? <= time and time <= ?"""
        self.cursor.execute(select_sql, (time, time + width))
        rec = self.cursor.fetchone()
        if rec is None:
            return None
        market_order_buy = rec[0]

        select_sql = """select min(fix_order_buy) from order_book where ? <= time and time <= ?"""
        self.cursor.execute(select_sql, (time, time + width))
        rec = self.cursor.fetchone()
        if rec is None:
            return None
        fix_order_buy = rec[0]

        return market_order_sell, market_order_buy, fix_order_sell, fix_order_buy

    def update_all_best_action(self, force=False):
        if force:
            time_sql = """select time from order_book"""
        else:
            time_sql = """select time from order_book where ba is NULL"""

        update_sql = """update order_book set ba = ? where time = ?"""

        self.cursor.execute(time_sql)

        for rec in self.cursor.fetchall():
            time = rec[0]

            rec = self.select_order_prices(time)
            if rec is None:
                continue

            market_order_sell, market_order_buy, fix_order_sell, fix_order_buy = rec

            rec = self.select_best_order_prices(time + 10, FORECAST_TIME)
            if rec is None:
                continue

            market_order_sell_f, market_order_buy_f, fix_order_sell_f, fix_order_buy_f = rec

            best_action = self.best_action(market_order_sell, market_order_buy, fix_order_sell, fix_order_buy, market_order_sell_f, market_order_buy_f, fix_order_sell_f, fix_order_buy_f)

            if best_action != ACTION.NOP:
                print(time, ' ', end='')
                print("fob  {}, mob  {}, fos  {}, mos  {} / ".format(fix_order_buy, market_order_buy, fix_order_sell, market_order_sell), end='')
                print("fobF {}, mobF {}, fosF {}, mosF {}".format(fix_order_buy_f, market_order_buy_f, fix_order_sell_f, market_order_sell_f), end='')

                if best_action == ACTION.SELL:
                    print(' sell', end='')
                if best_action == ACTION.SELL_NOW:
                    print(' SELL', end='')
                if best_action == ACTION.BUY:
                    print(' buy', end='')
                if best_action == ACTION.BUY_NOW:
                    print(' BUY', end='')

                print("")

            self.cursor.execute(update_sql, (best_action, time))


    def best_action(self, market_order_sell, market_order_buy, fix_order_sell, fix_order_buy, market_order_sell_f,
                        market_order_buy_f, fix_order_sell_f, fix_order_buy_f):


        if market_order_sell:
            market_order_sell = market_order_sell * TAKER_SELL

        if market_order_sell_f:
            market_order_sell_f = market_order_sell_f * TAKER_SELL

        if market_order_buy:
            market_order_buy = market_order_buy * TAKER_BUY

        if market_order_buy_f:
            market_order_buy_f = market_order_buy_f * TAKER_BUY

        if fix_order_sell:
            fix_order_sell = fix_order_sell * MAKER_SELL

        if fix_order_sell_f:
            fix_order_sell_f = fix_order_sell_f * MAKER_SELL

        if fix_order_buy:
            fix_order_buy = fix_order_buy * MAKER_BUY

        if fix_order_buy_f:
            fix_order_buy_f = fix_order_buy_f * MAKER_BUY

        action = ACTION.NOP

        if market_order_sell:
            if fix_order_buy_f:
                if market_order_sell > fix_order_buy_f + PRICE_MARGIN:
                    action = ACTION.SELL_NOW
            if market_order_buy_f:
                if market_order_sell > market_order_buy_f + PRICE_MARGIN:
                    action = ACTION.SELL_NOW

        if fix_order_sell:
            if fix_order_buy_f:
                if fix_order_sell > fix_order_buy_f + PRICE_MARGIN:
                    action = ACTION.SELL
            if market_order_buy_f:
                if fix_order_sell > market_order_buy_f + PRICE_MARGIN:
                    action = ACTION.SELL

        if market_order_buy:
            if fix_order_sell_f:
                if market_order_buy + PRICE_MARGIN < fix_order_sell_f:
                    action = ACTION.BUY_NOW
            if market_order_sell_f:
                if market_order_buy + PRICE_MARGIN < market_order_sell_f:
                    action = ACTION.BUY_NOW

        if fix_order_buy:
            if fix_order_sell_f:
                if fix_order_buy + PRICE_MARGIN < fix_order_sell_f:
                    action = ACTION.BUY
            if market_order_sell_f:
                if fix_order_buy + PRICE_MARGIN < market_order_sell_f:
                    action = ACTION.BUY

        return action


    def skip_nop_close_to_action(self):
        clear_sql = """update order_book set ba = NULL where time = ?"""

        start_time, end_time = self.get_db_info()

        time = start_time
        skip_flag = 0
        skip_number = 0
        while time <= end_time:
            best_action = self.select_best_action(time)
            if best_action is None:
                time += 1
                continue

            best_action_next = self.select_best_action(time + ORDER_TIME_WIDTH)

            if best_action != ACTION.NOP or best_action_next != ACTION.NOP:
                skip_flag = ORDER_TIME_WIDTH

            if skip_flag and best_action == ACTION.NOP:
                skip_number += 1

                self.cursor.execute(clear_sql, (time,))

            if skip_flag:
                skip_flag -= 1

            time += 1

        return skip_number


    def action_stat(self):
        sql = '''select ba, count(*) from order_book group by ba'''

        self.cursor.execute(sql)

        records = self.cursor.fetchall()

        return records

    def calc_latest_time(self):
        time_sql = """select time from order_book order by time desc"""

        self.cursor.execute(time_sql)

        records = self.cursor.fetchone()

        return records[0]

    def copy_db(self, source, destination, start_time=None, end_time=None):
        self.copy_table('order_book', source, destination, start_time, end_time)
        self.copy_table('sell_trade', source, destination, start_time, end_time)
        self.copy_table('buy_trade', source, destination, start_time, end_time)
        self.copy_table('funding', source, destination, start_time, end_time)

    def copy_table(self, table_name, source, destination, start_time, end_time):
        conn = sqlite3.connect(destination)
        cu = conn.cursor()
        self.create()

        cu.execute("attach database '" + source + "'as source_db")

        where_statement = ""
        if start_time is not None:
            where_statement = " where {0} <= time".format(str(start_time))

        if end_time is not None:
            where_statement += " and time < {0} ".format(str(end_time))

        sql = "insert or replace into {0} select * from source_db.{1}".format(table_name, table_name) + where_statement

        cu.execute(sql)
        conn.commit()

        cu.execute("detach database source_db")
        conn.commit()

    def import_db(self, file='/tmp/bitlog.db', start_time=None, end_time=None):
        self._create_table(self.cursor)

        self.import_table('order_book', file, start_time, end_time)
        self.import_table('sell_trade', file, start_time, end_time)
        self.import_table('buy_trade', file, start_time, end_time)
        self.import_table('funding', file, start_time, end_time)

        self.commit()

    def import_table(self, table_name, source, start_time=None, end_time=None):
        self.cursor.execute("attach database '" + source + "'as source_db")

        where_statement = ""
        if start_time is not None:
            where_statement = " where {0} <= time".format(str(start_time))

        if end_time is not None:
            where_statement += " and time < {0} ".format(str(end_time))

        sql = "insert or replace into {0} select * from source_db.{1}".format(table_name, table_name) + where_statement

        self.cursor.execute(sql)

        self.commit()

        self.cursor.execute("detach database source_db")

        print('import table', table_name, source)

    def import_dump_file(self, file='/tmp/bitlog.dump'):
        with open(file) as f:
            for line in f:
                self.connection.executescript(line)
                print(line)

    def get_db_info(self):
        sql = "select time from order_book order by time asc"
        cur = self.connection.execute(sql)
        start_time = cur.fetchone()[0]
        print(start_time)

        sql = 'select time from order_book order by time desc'
        cur = self.connection.execute(sql)
        end_time = cur.fetchone()[0]
        print(end_time)

        return start_time, end_time

    def list_price(self, *, start_time=None, end_time=None, desc=False):
        if start_time and end_time:
            sql = """select time, market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time,  
                   fix_order_buy, fix_order_buy_time from order_book where ? <= time and time <= ? order by time"""
            if desc:
                sql += ' desc'
            cur = self.connection.execute(sql, (start_time, end_time,))
        else:
            sql = """select time, market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time,  
                   fix_order_buy, fix_order_buy_time from order_book order by time"""
            if desc:
                sql += ' desc'
            cur = self.connection.execute(sql)
        return cur.fetchall()

    @lru_cache(maxsize=2048)
    def select_q_val(self, time, start_time, start_action):
        rec = self.select_q(time, start_time, start_action)
        q = None

        if rec:
            q = QValue()
            q.set_q_records(rec)

        # print('selectq', time, start_time, start_action, q)

        return q

    def select_q(self, time, start_time, start_action):
        '''
        select and return q values
        :param time: time to select
        :param start_time: original time the action was executed(if the time and the start_time is same, the action is not executed yet)
        :param start_action: action executed at original time(NOP is for action is not executed yet)
        :return:
        '''
        select_q_sql = """select time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q
                            from q where ? <= time and ? <= start_time and start_action = ? order by start_time, time limit 10 
        """
        if start_action == ACTION.NOP:
            start_time = 0

#        cur = self.connection.cursor()
#        cur.execute(select_q_sql, (time, start_time, start_action))
#        rec = cur.fetchone()

        #self.cursor.execute(select_q_sql, (time, start_time, start_action))
        #rec = self.cursor.fetchone()

        select_q_sql_s = """select time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q
                            from q where {} <= time and {} <= start_time and start_action = {} order by start_time, time limit 10 
        """.format(time, start_time, start_action)

        self.cursor.execute(select_q_sql_s)
        rec = self.cursor.fetchone()

        return rec

    def insert_q(self, *, time, start_time, start_action, q_value: QValue):
        sql = '''INSERT or REPLACE into q
                      (time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q)
                      values(?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, [time, start_time, start_action,
                                  q_value.q[ACTION.NOP], q_value.q[ACTION.BUY], q_value.q[ACTION.BUY_NOW],
                                  q_value.q[ACTION.SELL], q_value.q[ACTION.SELL_NOW]])

    def list_q(self, start_time, start_action, asc=True):
        '''
        :param start:
        :param start_action:
        :param start_time:
        :return:
        '''

        if asc:
            select_q_sql = """select time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q
                            from q where start_time = ? and start_action = ? order by time 
            """
        else:
            select_q_sql = """select time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q
                                from q where start_time = ? and start_action = ? order by time desc 
            """

        self.cursor.execute(select_q_sql, (start_time, start_action,))
        rec = self.cursor.fetchall()

        return rec

    def update_q_on_nop(self):
        q_list = self.list_q(start_time=0, start_action=ACTION.NOP, asc=False)

        last_q = None

        for q_rec in q_list:
            q = QValue()
            q.set_q_records(q_rec)

            if last_q:
                t = last_q.time - q.time
                last_max_q = last_q.max_q() * Q_FIRST_DISCOUNT_RATE * (Q_DISCOUNT_RATE ** t)

                q[ACTION.NOP] = last_max_q
                self.insert_q(time=q.time, start_time=0, start_action=ACTION.NOP, q_value=q)

            last_q = q

        self.commit()

    def select_q_values(self, time, action):
        '''
        :param time time to select
        :param action
        :return: q values for NOP, buy, sell, BUY, SELL
        '''
        select_q_sql = """select time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q
                                from q where start_time = ? and start_action= ? order by start_time, time
            """
        self.cursor.execute(select_q_sql, (time,action, ))
        rec = self.cursor.fetchone()

        q = QValue()
        q.set_q_records(rec)

        return q

    '''
    def insert_q_sequence(self, q_sequence):
        for q in q_sequence.q_values:
            self.insert_q(start_time=q_sequence.start_time, time=q.order_prices.time,
                          start_action=q_sequence.action, q_value=q)

        self.commit()
    '''

    def insert_updated_q(self):
        '''
        update q values according to the list of prices
        :return: None
        '''
        old_price = None

        for line in self.list_price():
            price = OrderPrices()
            price.set_price_record(line)
            q_val = QValue()

            if old_price and (not old_price.is_equal_prices(price)):
                print(old_price.time)
                # update
                if old_price.market_order_sell:
                    q = self.create_q_sequence(start_time=old_price.time, action=ACTION.SELL_NOW,
                                           start_price=old_price.market_order_sell, skip_time=60)
                    q_val[ACTION.SELL_NOW] = q

                if old_price.market_order_buy:
                    q = self.create_q_sequence(start_time=old_price.time, action=ACTION.BUY_NOW,
                                           start_price=old_price.market_order_buy, skip_time=60)
                    q_val[ACTION.BUY_NOW] = q

                if old_price.fix_order_sell:
                    q = self.create_q_sequence(start_time=old_price.time, action=ACTION.SELL,
                                           start_price=old_price.fix_order_sell, skip_time=60)
                    q_val[ACTION.SELL] = q

                if old_price.fix_order_buy:
                    q = self.create_q_sequence(start_time=old_price.time, action=ACTION.BUY,
                                           start_price=old_price.fix_order_buy, skip_time=60)
                    q_val[ACTION.BUY] = q

                self.insert_q(time=old_price.time, start_action=ACTION.NOP, start_time=0, q_value=q_val)

            old_price = price

    def select_highest_price_time(self, time):
        sql = """select time, market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time,  
               fix_order_buy, fix_order_buy_time from order_book where ? <= time and time < ? 
               order by market_order_buy desc, time"""

        self.cursor.execute(sql, (time, time + HOLD_TIME_MAX))
        rec = self.cursor.fetchone()
        price = OrderPrices(rec)

        return price

    def select_lowest_price_time(self, time):
        sql = """select time, market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time,  
               fix_order_buy, fix_order_buy_time from order_book where ? <= time and time < ? 
               order by market_order_sell, time"""

        self.cursor.execute(sql, (time, time + HOLD_TIME_MAX))
        rec = self.cursor.fetchone()
        price = OrderPrices(rec)

        return price

    def create_q_sequence(self, *, start_time, action, start_price, skip_time=0):
        if (action == ACTION.BUY) or (action == ACTION.BUY_NOW):
            peak_price = self.select_highest_price_time(start_time + EXECUTE_TIME_MIN)
        elif (action == ACTION.SELL) or (action == ACTION.SELL_NOW):
            peak_price = self.select_lowest_price_time(start_time + EXECUTE_TIME_MIN)

        prices = self.list_price(start_time=start_time+skip_time, end_time=peak_price.time, desc=True)

        nop_q = 0
        old_q = QValue(start_time=start_time, start_action=action, start_price=start_price)

        skip_count = 0
        for price_rec in prices:
            q = QValue(start_time=start_time, start_action=action, start_price=start_price)
            q.set_price_record(price_rec)
            nop_q *= Q_DISCOUNT_RATE

            if q.is_same_q_exept_nop(old_q):
                skip_count += 1
                continue

            action = old_q.get_best_action()

            if(action == ACTION.BUY or action == ACTION.SELL):
                new_q = old_q.max_q() * Q_FIRST_DISCOUNT_RATE * (Q_DISCOUNT_RATE ** skip_count)
            else:
                new_q = old_q.max_q() * (Q_DISCOUNT_RATE ** skip_count)
            skip_count = 0

            if nop_q < new_q:
                nop_q = new_q
            q[ACTION.NOP] = nop_q

            if q.time != start_time:
                self.insert_q(time=q.time, start_time=start_time, start_action=action, q_value=q)

            old_q = q

        self.commit()

        return old_q.max_q()

    def update_all_q(self):
        '''
        update all q values according to existing q values
        :return:
        '''
        self.insert_updated_q()
        self.update_q_on_nop()

