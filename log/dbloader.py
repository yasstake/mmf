import sys
import glob
from log.logdb import LogDb
from log.loader import LogLoader

class DbLoader:
    def __init__(self):
        self.book_last_time = 0
        self.funding_last_time = 0
        self.trade_last_time = 0
        self.log_db = None

    def load(self, log_dir = '/tmp', db_file="/tmp/bitlog.db"):
        self.log_db = LogDb(db_file)
        self.log_db.connect()
        self.log_db.create()

        log_files = glob.glob(log_dir + '/' + '*.log')

        log_loader = LogLoader(self.order_book_tick,  self.trade_tick, self.funding_tick)

        for file in log_files:
            print(file)
            log_loader.load(file)

        self.log_db.close()

    def order_book_tick(self, time_stamp, order_book):
        if self.book_last_time != time_stamp:
            self.log_db.insert_order_book(time_stamp, order_book)
        self.book_last_time = time_stamp

    def funding_tick(self, time_stamp, funding):
        print("funding", time_stamp, funding)
        self.log_db.insert_funding(time_stamp, funding)

    def trade_tick(self, time_stamp, buy_trade, sell_trade):
        for price in buy_trade.keys():
            self.log_db.insert_buy_trade(time_stamp, price, buy_trade[price])

        for price in sell_trade.keys():
            self.log_db.insert_sell_trade(time_stamp, price, sell_trade[price])

if __name__ == '__main__':
    log_dir = '/tmp'
    db_file = '/tmp/bitlog.db'

    if len(sys.argv) == 2:
        log_dir = sys.argv[0]
        db_file = sys.argv[1]

        print(log_dir, db_file)

    db_loader = DbLoader()
    db_loader.load(log_dir, db_file)


