import sys
import glob
from log.logdb import LogDb
from log.loader import LogLoader
from gcp.storage import LogStorage
from log.timeutil import timestamp

class DbLoader:
    def __init__(self):
        self.book_last_time = 0
        self.funding_last_time = 0
        self.trade_last_time = 0
        self.log_db = None
        self.log_loader = LogLoader(self.order_book_tick,  self.trade_tick, self.funding_tick)

    def open_db(self, db_file=None):
        self.log_db = LogDb(db_file)
        self.log_db.connect()
        self.log_db.create_cursor()
        self.log_db.create()

    def close_db(self):
        self.log_db.close()

    def get_db(self):
        return self.log_db

    def load_line(self, line):
        self.log_loader.load_line(line)

    def load_lines(self, lines):
        for line in lines:
            self.log_loader.load_line(line)

    def load_file(self, log_file):
        print('Processs ' + log_file, end='')
        try:
            self.log_loader.load(log_file)
        except EOFError as e:
            print('error to process fileError EOF', e)
        except Exception as e:
            print('File process error SKIP', e)

    def load_dir(self, log_dir ='/tmp'):
        log_files = sorted(glob.glob(log_dir + '/' + '*.log'))
        for file in log_files:
            self.log_db.create_cursor()
            self.load_file(file)
            self.log_db.commit()

        log_files = sorted(glob.glob(log_dir + '/' + '*.log.gz'))
        for file in log_files:
            self.log_db.create_cursor()
            self.load_file(file)
            self.log_db.commit()

    def load_from_blobs(self, path=''):
        log_storage = LogStorage()

        log_storage.process_blob_dir(path, self.load_file)

    def load_from_blob_by_date(self, year, month, day):
        log_storage = LogStorage()

        log_storage.process_blob_date_with_padding(year, month, day, self.load_file)

    def order_book_tick(self, time_stamp, order_book):
        if self.book_last_time != time_stamp:
            self.log_db.insert_order_book_message(time_stamp, order_book)
        self.book_last_time = time_stamp

    def funding_tick(self, time_stamp, funding):
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
    db_loader.open_db()
    db_loader.load_dir(log_dir)
    db_loader.close_db()


