import unittest

import numpy as np
from matplotlib import pylab as plt

from log.logdb import LogDb
from log.price import PriceBoard
from log.price import PriceBoardDB
from log.timeutil import *


class MyTestCase(unittest.TestCase):
    def test_add_buy_order(self):
        board = PriceBoard()
        board.current_time = 1000
        board.add_buy_trade(1000, 1, 1)   # in BTC
        board.add_buy_trade(1000, 1, 1)   # in BTC


    def test_add_sell_order(self):
        board = PriceBoard()
        board.current_time = 1000
        board.add_sell_trade(999, 1, 1)   # in BTC
        board.add_sell_trade(999, 1, 1)   # in BTC

    def test_set_center_price(self):
        PRICE = 4000.5
        board = PriceBoardDB()
        board.set_center_price(PRICE)
        price = board.get_center_price()
        self.assertEqual(price, PRICE)

    def test_current_time(self):
        board = PriceBoardDB()
        board.set_origin_time(1000)
        time = board.get_origin_time()
        self.assertEqual(1000, time)

    def test_get_positoin(self):
        board = PriceBoardDB()
        board.set_origin_time(1000)
        board.set_center_price(1000)

        x, y = board.get_position(999, 1000.5)
        self.assertEqual(x, 1)
        self.assertEqual(y, 17)

        x, y = board.get_position(1000, 1000)
        self.assertEqual(x,0)
        self.assertEqual(y, 16)

    def test_save(self):
        board = PriceBoardDB()

        board.save("/tmp/boarddump.npz")

    def test_save_tf_record(self):
        board = PriceBoardDB()

        board.normalize()

        board.save_tf_record()
    #        board.save_tf_record('gs://mmflog/data.tfrecords')


    def test_load_tf_record(self):
        board = PriceBoardDB()

        board.load_tf_record()


    def test_load_tf_records(self):
        PriceBoardDB.export_board_to_blob()

    def test_load_tf_records_with_time(self):
        db = LogDb()
        db.connect()
        db.create_cursor()

        db.import_db()

        time = 1552910400
        PriceBoardDB.export_db_to_blob_with_time(db, time, width=600, root_dir='/tmp/')

    #        db.close()

    def test_load_tf_records_with_time_from_file(self):
        db = LogDb('/tmp/bitlog.db')
        db.connect()
        db.create_cursor()

        time = 1552957717

        PriceBoardDB.export_db_to_blob_with_time(db, time, width=600, root_dir='/tmp/')

    #        db.close()

    def test_load_from_db_one_rec(self):
        end_time = self.calc_end_time() - 600

        board = self._load_from_db_one_rec_with_time(end_time)

        print('sell_book_price', board.sell_book_price)
        print('sell_book_vol', board.sell_book_vol)
        print('sell_book_price', board.buy_book_price)
        print('buy_book_vol', board.buy_book_vol)
        print('sell_trade_price', board.sell_trade_price)
        print('sell_trade_volume', board.sell_trade_volume)
        print('buy_trade_price', board.buy_trade_price)
        print('buy_trace_volume', board.buy_trade_volume)


    def _load_from_db_one_rec_with_time(self, time):

        board = PriceBoardDB.load_from_db(time)

        sell_board = board.sell_order

        max_x, max_y = sell_board.shape
        print(max_x, max_y)

        for x in range(1, max_x):
            line = False
            for y in range(1, max_y):
                if sell_board[x, y]:
                    line = True
                    break;

            if line is False:
                print("error", x, y)
                self.assertFalse("empty line in order book")
                break;

        for x in range(0, max_x):
            print(time - x, ' ', end='')
            for y in range(0, max_y):
                if sell_board[x, y]:
                    print('X', end='')
                else:
                    print('.', end='')
            print('', end='\n')
        print(board)

        return board

    def test_load_from_db_one(self):
        end_time = self.calc_end_time()

        t = end_time

        writer = PriceBoardDB.get_tf_writer('/tmp/onedata.tfrecords')
        board = PriceBoardDB.load_from_db(t)
        board.save_tf_to_writer(writer)
        writer.close()

    def test_load_from_db_600(self):
        end_time = self.calc_end_time()

        t = end_time

        db = LogDb('/tmp/bitlog.db')
        db.connect()
        db.create_cursor()

        writer = PriceBoardDB.get_tf_writer('/tmp/600rec.tfrecords')

        retry = 600
        while retry:
            board = PriceBoardDB.load_from_connected_db(t-retry, db)

            if board:
                board.save_tf_to_writer(writer)
                break

            retry -= 1

        db.close()
        writer.close()

    def test_load_from_db(self):
        end_time = self.calc_end_time()

        t = end_time

        t = 1553302179 # ba = 1
        #t = 1553276602 # ba = 2
        #t = 1553301395 # ba = 3
        #        t = 1552695458

        board = PriceBoardDB.load_from_db(t)

        fig = plt.figure()

        fig.text(0.1, 0.1, board.best_action)

        array = board.buy_order
        sub = fig.add_subplot(2, 2, 1)
        sub.matshow(array, vmin=0, vmax=255)

        array = board.sell_order
        sub = fig.add_subplot(2, 2, 2)
        sub.matshow(array, vmin=0, vmax=255)


        array = board.buy_trade
        sub = fig.add_subplot(2, 2, 3)
        sub.matshow(array, vmin=0, vmax=100)

        array = board.sell_trade
        sub = fig.add_subplot(2, 2, 4)
        sub.matshow(array, vmin=0, vmax=100)

        fig.show()

        print(board.best_action)


    def calc_end_time(self):
        db = LogDb("/tmp/bitlog.db")
        db.connect()
        db.create_cursor()

        return int(db.get_db_info()[1])

    def test_db_stat_time(self):
        DAY_MIN = 24 * 60 * 60

        board = PriceBoardDB()

        start_time, end_time = board.start_time()

        start_midnight = (int(start_time / (DAY_MIN)) + 1) * DAY_MIN
        end_midnight = (int(end_time / (DAY_MIN))) * DAY_MIN -1

        print(start_time, end_time, start_midnight, end_midnight)

        if(start_time < start_midnight and end_midnight < end_time):
            print('good data')
            # todo do something

        width = end_midnight - start_midnight

        time  = start_midnight
        while time < end_midnight:
            file = (int(time/60)*60)

            if file == time:
                file_path = date_string(file, '/')
                print(file_path, time_stamp_string(time))

            time += 1



    def test_load_from_db_normalize(self):
        end_time = self.calc_end_time()

        print("time->", end_time)

        t = end_time

        board = PriceBoardDB.load_from_db(t)

        plt.imshow(board.buy_order, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.sell_order, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.buy_trade, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.sell_trade, vmin=0, vmax=200)
        plt.figure()
        plt.show()

    def test_load_from_db_and_save_to_file(self):
        end_time = self.calc_end_time()

        t = end_time
        board = PriceBoardDB.load_from_db(t)

        board.save("/tmp/board")


    def test_load_from_db_normalize2(self):
        end_time = self.calc_end_time()

        t = end_time

        board = PriceBoardDB.load_from_db(t)

    def test_load_from_db_normalize3(self):
        end_time = self.calc_end_time()

        t = end_time

        while True:
            board = PriceBoardDB.load_from_db(t)
            print("time->", t)
            if not board:
                break
            t = t+1

    def test_save_to_tf_record(self):
        PriceBoardDB.export_board_to_blob()


    def test_calc_variance(self):
        a = np.array([[0.1, 0, 0, 0, 1],
                     [0, 0, 1, 0, 2],
                     [0, 0, 1, 0, 3],
                     [0, 0, 0, 0, 4]])

        print(a)

        non_zero_count = np.nonzero(a)[0].size
        sum_a   = np.sum(a)
        mean = sum_a/non_zero_count

        print("average", sum_a/non_zero_count, sum_a, non_zero_count)

        b = np.square(a)
        square_sum_a = np.sum(b)

        print("square average", square_sum_a/non_zero_count, square_sum_a, non_zero_count)

        s = square_sum_a/non_zero_count - (sum_a/non_zero_count)**2

        # standard dev(non zero factor only)
        print(s**0.5)

        board = PriceBoardDB()
        mean2, stddev2 = board.calc_static(a)
        self.assertEqual(mean, mean2)
        self.assertEqual(s**0.5, stddev2)

        # clipping 3
        c = np.clip(a, 0, 3)
        print(c)

        d = np.ceil(a)
        print(d)

        e = (a / 3)*255
        f = np.ceil(np.clip(e, 0, 255))
        print(f)

        g = f.astype('uint8')

        print(g)

    def test_save_to_img(self):
        end_time = self.calc_end_time()

        t = end_time

        PriceBoardDB.save_to_img(end_time, '/tmp/')

if __name__ == '__main__':
    unittest.main()
