import os
import numpy as np
import tensorflow as tf
from matplotlib import pylab as plt

from log.timeutil import *
import log.logdb as logdb;
from log.constant import *


class PriceBoard:
    """
    represent order book board and its history

    Layer 1   Buy order     (0 edge)
    Layer 2   Sell Order    (other side)
    Layer 3   Buy Trade & funding minus (0 edge)
    Layer 4   Sell Trade & funding plus (other side)

    """
    def __init__(self):
        self.current_time = 0
        self.center_price = 0

        self.sell_trade = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.buy_trade = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.sell_order = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))
        self.buy_order = np.zeros((BOARD_TIME_WIDTH, BOARD_WIDTH))

        self.my_sell_order = {}
        self.my_buy_order = {}

        self.market_sell_price = 0
        self.market_buy_price = 0

        self.fix_sell_price = 0
        self.fix_buy_price = 0

        self.funding_ttl = 0
        self.funding = 0

        self.best_action = ACTION.NOP
        self.ba_nop = 0
        self.ba_sell = 0
        self.ba_buy = 0
        self.ba_sell_now = 0
        self.ba_buy_now =0

    def get_board(self):
        board = np.stack([self.buy_order, self.sell_order, self.buy_trade, self.sell_trade])
        return board

    def add_sell_order(self, price, size):
        if price in self.my_sell_order:
            self.my_sell_order[price] += size
        else:
            self.my_sell_order[price] = size

    def add_buy_order(self, price, size):
        if price in self.buy_order:
            self.my_buy_order[price] += size
        else:
            self.my_buy_order[price] = size

    def set_origin_time(self,time):
        self.current_time = time

    def get_origin_time(self):
        return self.current_time

    def set_center_price(self, price):
        self.center_price = price

    def get_center_price(self):
        return self.center_price

    BOARD_CENTER = BOARD_WIDTH / 2

    def get_position(self, time, price):
        p = int((price - self.center_price) / PRICE_UNIT + PriceBoardDB.BOARD_CENTER)

        if p < 0 or BOARD_WIDTH <= p:
            return None

        t = int(self.current_time - time)

        return t, p

    def set_sell_order_book(self, time, price, line):
        width = 0

        for vol in line:
            pos = self.get_position(time, price)
            if not pos:
                break

            t, p = pos
            self.sell_order[t, p] = vol
            price += PRICE_UNIT
            width += 1

            if BOARD_WIDTH < width:
                break

    def set_buy_order_book(self, time, price, line):
        width = 0

        for vol in line:
            pos = self.get_position(time, price)

            if not pos:
                break

            t, p = pos
            self.buy_order[t, p] = vol

            price -= PRICE_UNIT
            width += 1
            if BOARD_WIDTH < width:
                break

    def add_buy_trade(self, time, price, volume, window=1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.buy_trade[t][p] = self.buy_trade[t][p] + volume / window

    def add_sell_trade(self, time, price, volume, window=1):
        pos = self.get_position(time, price)
        if pos:
            t, p = pos
            self.sell_trade[t][p] = self.sell_trade[t][p] + volume / window

    def set_funding(self, ttl, funding):
        print("fundig->", ttl, funding)
        self.funding = funding
        self.funding_ttl = ttl

    def save(self, filename):
        #todo: not implemented
        print("---dummy---")
        np.save(filename + "sell_order", self.sell_order)
        np.save(filename + "buy_order", self.buy_order)
        np.save(filename + "buy_trade", self.buy_trade)
        np.save(filename + "sell_trade", self.sell_trade)

        np.savez_compressed(filename + "sell_order", self.sell_order)
        np.savez_compressed(filename + "buy_order", self.buy_order)
        np.savez_compressed(filename + "buy_trade", self.buy_trade)
        np.savez_compressed(filename + "sell_trade", self.sell_trade)

        #np.savez_compressed(filename, self.data)

    def feature_int64(self, a):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[a]))

    def feature_float(self, a):
        return tf.train.Feature(float_list=tf.train.FloatList(value=[a]))

    def feature_bytes(self, a):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[a]))

    @staticmethod
    def get_tf_writer(output_file='/tmp/data.tfrecords'):
        pio = tf.python_io
        writer = pio.TFRecordWriter(str(output_file), options=pio.TFRecordOptions(pio.TFRecordCompressionType.GZIP))

        return writer

    def save_tf_record(self, output_file='/tmp/data.tfrecords'):
        writer = PriceBoard.get_tf_writer(output_file)
        self.save_tf_to_writer(writer)
        writer.close()

    def save_tf_to_writer(self, writer):
        record = self._tf_example_record()

        writer.write(record.SerializeToString())


    def _tf_example_record(self):
        board = np.stack([self.buy_order, self.sell_order, self.buy_trade, self.sell_trade])

        record = tf.train.Example(features=tf.train.Features(feature={
            'board': self.feature_bytes(board.tobytes()),
            'market_buy_price': self.feature_float(self.market_buy_price),
            'market_sell_price': self.feature_float(self.market_sell_price),
            'fix_buy_price': self.feature_float(self.fix_buy_price),
            'fix_sell_price': self.feature_float(self.fix_sell_price),
            'ba': self.feature_int64(self.best_action),
            'ba_nop': self.feature_int64(self.ba_nop),
            'ba_sell': self.feature_int64(self.ba_sell),
            'ba_buy': self.feature_int64(self.ba_buy),
            'ba_sell_now': self.feature_int64(self.ba_sell_now),
            'ba_buy_now': self.feature_int64(self.ba_buy_now),
            'time': self.feature_int64(self.current_time)
            }))

        return record


    def calc_static(self, a):
        """
        calc matrix non zero mean and stddev
        :param a: matrix to be examine
        :return: mean, stddev
        """
        item_no = np.nonzero(a)[0].size
        non_zero_sum = np.sum(a)
        non_zero_sq_sum = np.sum(np.square(a))

        variant = non_zero_sq_sum / item_no - (non_zero_sum / item_no)**2

        return non_zero_sum/item_no, variant ** 0.5

    def normalize(self):
        order_mean, order_stddev = self.calc_static(self.sell_order + self.buy_order)
        trade_mean, trade_stddev = self.calc_static(self.sell_trade + self.buy_trade)

        self.buy_order = self.normalize_array(self.buy_order, order_mean + order_stddev / 2)
        self.sell_order = self.normalize_array(self.sell_order, order_mean + order_stddev / 2)

        self.buy_trade = self.normalize_array(self.buy_trade, trade_mean + trade_stddev)
        self.sell_trade = self.normalize_array(self.sell_trade, trade_mean + trade_stddev)

    def normalize_array(self, array, max_value):
        float_array = array * (256 / max_value)
        uint8_array = np.ceil(np.clip(float_array, 0, 255)).astype('uint8')

        return uint8_array


class PriceBoardDB(PriceBoard):
    @staticmethod
    def export_board_to_blob(start_time=None, end_time=None, db_object=None, root_dir='/tmp'):
        DAY_MIN = 24 * 60 * 60

        board = PriceBoardDB()

        if start_time is None or end_time is None:
            db_start_time, db_end_time = board.start_time()

            start_time = (int(db_start_time / (DAY_MIN)) + 1) * DAY_MIN
            end_time = (int(db_end_time / (DAY_MIN))) * DAY_MIN

            print(start_time, end_time, db_start_time, db_end_time)

            if not (db_start_time < start_time and end_time < db_end_time):
                print('wrong data')
                # todo do something
                return None

        if db_object is None:
            db = logdb.LogDb('/tmp/bitlog.db')
            db.connect()
            db.create_cursor()
        else:
            db = db_object

        PriceBoardDB.export_db_to_blob(db, start_time, end_time, root_dir)

        if db_object is None:
            db.close()

    @staticmethod
    def export_db_to_blob(db, start_time, end_time, root_dir='/tmp'):
        BOARD_IN_FILE = 600

        time = start_time

        while time < end_time:
            last_board = PriceBoardDB.export_db_to_blob_with_time(db, time, BOARD_IN_FILE, root_dir)

            if last_board is None:
                print('error to export board', time)
            time += BOARD_IN_FILE


    @staticmethod
    def export_db_to_blob_with_time(db, start_time, width, root_dir):
        time = start_time
        end_time = start_time + width

        tf_writer = None
        while time < end_time:

            file = (int(time / width) * width)

            board = PriceBoardDB.load_from_connected_db(time, db)

            if not board:
                time += 1
                print("ERROR to skip load", time)
                continue

            if board and file == time or tf_writer is None:
                if tf_writer:
                    tf_writer.close()

                time_object = time_stamp_object(time)

                file_dir = root_dir + '/{:04d}/{:02d}/{:02d}'.format(time_object.year, time_object.month, time_object.day)
                if root_dir.startswith('/') and not os.path.exists(file_dir):
                    os.makedirs(file_dir)

                file_path = file_dir + '/{:010d}-{:02d}-{:02d}-{:02d}-{:02d}.{:02d}.tfrecords'.format(time, time_object.month, time_object.day, time_object.hour, time_object.minute, board.best_action)

                print(time, file_path)
                tf_writer = PriceBoard.get_tf_writer(file_path)

            time += 1


            board.save_tf_to_writer(tf_writer)


        if tf_writer:
            tf_writer.close()

        return board


    @staticmethod
    def start_time(db=None):
        if db is None:
            db = logdb.LogDb('/tmp/bitlog.db')
            db.connect()
            db.create_cursor()

        start_time, end_time = db.get_db_info()

        return start_time, end_time

    @staticmethod
    def end_time():
        pass

    @staticmethod
    def load_from_db(time, db_name = "/tmp/bitlog.db"):
        db = logdb.LogDb(db_name)
        db.connect()
        db.create_cursor()

        board = PriceBoardDB.load_from_connected_db(time, db)

        db.close()
        return board


    @staticmethod
    def load_from_connected_db(time, db):

        board = PriceBoardDB()

        board.set_origin_time(time)

        retry = 10
        center_price = None
        while retry:
            center_price = db.select_center_price(time)
            if center_price:
                break
            time = time + 1
            retry = retry - 1

        if not center_price:
            print('---DBEND---')
            return None

        board.set_center_price(center_price)

        error_count = 0
        query_time = time
        time_window = 1

        for offset in range(0, TIME_WIDTH):
            if not PriceBoardDB.load_from_db_time(db, board, time, offset, query_time, time_window):
                error_count = error_count + 1
            query_time = query_time - time_window

            if time - query_time < 8:
                pass
            elif time - query_time < 16:
                pass
            elif time - query_time < 32:
                pass
            elif time - query_time < 64:
                pass
            elif time - query_time < 128:
                pass
            else:
                pass

        board.normalize()

        #load prices
        prices = db.select_order_prices(time)
        if prices:
            market_order_sell, market_order_buy, fix_order_sell, fix_order_buy = prices

            board.market_sell_price = market_order_sell
            board.market_buy_price = market_order_buy

            if fix_order_sell:
                board.fix_sell_price = fix_order_sell

            if fix_order_buy:
                board.fix_buy_price = fix_order_buy

        #load funding
        funding = db.select_funding(time)

        if funding:
            t, p = funding
            board.funding_ttl = 0
            board.funding = 0

        #load action
        board.best_action = db.select_best_action(time)

        ba_nop, ba_buy, ba_buy_now, ba_sell, ba_sell_now = db.calc_best_actions(time)

        board.ba_nop = ba_nop
        board.ba_buy = ba_buy
        board.ba_buy_now = ba_buy_now
        board.ba_sell = ba_sell
        board.ba_sell_now = ba_sell_now

        if 10 < error_count:
            return None

        return board


    @staticmethod
    def load_from_db_time(db, board, time_origin, offset, query_time, time_window=1):

        #load sell order
        for t, price, volume in db.select_sell_trade(query_time, time_window):
            board.add_sell_trade(time_origin - offset, price, volume / time_window)

        #load buy order
        for t, price, volume in db.select_buy_trade(query_time, time_window):
            board.add_buy_trade(time_origin - offset, price, volume / time_window)

        #load order book
        order_book = None

        max_retry = 100
        if time_window < max_retry:
            max_retry = time_window + 50

        retry = 0
        while(not order_book and retry < max_retry):
            order_book = db.select_order_book(query_time - retry)
            retry = retry + 1


        if order_book:
            t, sell_min, sell_book, buy_max, buy_book = order_book
            board.set_sell_order_book(time_origin - offset, sell_min, sell_book)
            if(len(sell_book) < 10):
                print("shot->", time_origin - offset, sell_book)

            board.set_buy_order_book(time_origin - offset, buy_max, buy_book)

            return True
        else:
            print("NO ORDERBOOK FOUND->", query_time)
            return False

    @staticmethod
    def save_to_img(time, img_dir, db, frame_no = None):
        t = time

        board = PriceBoardDB.load_from_connected_db(time, db)

        fig = plt.figure()

        fig.text(0.05, 0.05, board.best_action, fontsize=28)

        fig.text(0.2, 0.05, board.market_buy_price)
        fig.text(0.4, 0.05, board.center_price)
        fig.text(0.6, 0.05, board.market_sell_price)

        array = board.buy_order
        sub = fig.add_subplot(1, 4, 1)
        sub.matshow(array, vmin=0, vmax=255)
        fig.text(0.15, 0.95, 'BUY BOOK')

        array = board.sell_order
        sub = fig.add_subplot(1, 4, 2)
        sub.matshow(array, vmin=0, vmax=255)
        fig.text(0.35, 0.95, 'SELL BOOK')

        array = board.buy_trade
        sub = fig.add_subplot(1, 4, 3)
        sub.matshow(array, vmin=0, vmax=100)
        fig.text(0.55, 0.95, 'BUY TRAN')

        array = board.sell_trade
        sub = fig.add_subplot(1, 4, 4)
        sub.matshow(array, vmin=0, vmax=100)
        fig.text(0.75, 0.95, 'SELL TRAN')

        if frame_no == None:
            img_file = img_dir + '/{:d}-{:02d}.png'.format(t, board.best_action)
        else:
            img_file = img_dir + '/{:06d}.png'.format(frame_no)

        plt.savefig(img_file)
        plt.close()

    @staticmethod
    def export_db_to_img(db_file, img_dir, frame_no = None):
        DAY_MIN = 24 * 60 * 60

        db = logdb.LogDb(db_file)
        db.connect()
        db.create_cursor()

        db_start_time, db_end_time = PriceBoardDB.start_time(db)

        print('time->', db_end_time)

        start_time = (int(db_start_time / (DAY_MIN)) + 1) * DAY_MIN
        end_time = (int(db_end_time / (DAY_MIN))) * DAY_MIN

        time = start_time

        print('time->', time)



        while time < end_time:
            print('db->', db)
            PriceBoardDB.save_to_img(time, img_dir, db, frame_no)
            time += 1

            if not frame_no == None:
                frame_no += 1

        db.close()

