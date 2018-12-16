
import sys
import os
import glob
import sqlite3
import log.bitws


DB_NAME = ":memory:"


class LogDb:
    def __init__(self, db_name = DB_NAME):
        self.db_name = db_name
        self.connection = None
        self.last_time = 0
        self.sell_min = 99999999
        self.buy_max = 0

        pass

    def __del__(self):
        self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)

    def create(self):
        '''create db'''
        cursor = self.connection.cursor()

        cursor.execute('''create table if not exists order_book (time integer, side integer, price real, size real) ''')
        cursor.execute(
            '''create table if not exists order_book_info
                    (time integer, sell_min real, sell_max real, sell_max_vol real, 
                     buy_min real, buy_max real, buy_max_vol real) ''')

        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def insert(self, time, message):
        print(time)


        for item in message:
            volume = item['size']
            price = item['price']

            if(item['side'] == 'Sell'):
                side = 0
                if (price < self.sell_min):
                    self.sell_min = price
            else:
                side = 1
                if(self.buy_max < price ):
                    self.buy_max = price

    def indert_db(self):
        cursor = self.connection.cursor()
#            cursor.execute('INSERT or replace into order_book values(?,?,?,?)', [time, side, item['size'], item['price']])

        cursor.execute('INSERT or replace into order_book_info values(?,?,?,?,?,?,?)',[time, sell_min, sell_max, sell_max_vol, buy_min, buy_max, buy_max_vol])
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

