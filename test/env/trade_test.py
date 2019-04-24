import glob
import unittest

import tensorflow as tf

from env.trade import Trade

tf.enable_v2_behavior()


class MyTestCase(unittest.TestCase):

    def test_list_files(self):
        trade = Trade()

        list = trade.list_tfdata_list()
        print(list)

        print('number of files->', trade.number_of_files)


    def test_glob_files(self):
        files = glob.glob('/bitlog/**/*.tfrecords', recursive=True)

        print(files)
        print(sorted(files))


    def test_new_episode_files(self):
        trade = Trade()

        files = trade._new_episode_files()
        print(files)

    def test_skip_count(self):
        trade = Trade()

        print(trade._skip_count())

    def test_new_episode(self):
        trade = Trade()

        trade.new_episode()

        result = trade.new_sec()

        print(result)

        print(trade.time)

    def test_new_sec(self):
        trade = Trade()

        trade.new_episode()

        trade.new_sec()
        print(trade.time)


        trade.new_sec()
        print(trade.time)

        trade.new_sec()
        print(trade.time)

        trade.new_sec()
        print(trade.time)


    def test_read_one_episode(self):
        trade = Trade()

        trade.new_episode()

        num_of_records = 0

        while trade.new_sec():
            self.assertIsNotNone(trade.board)
            self.assertIsNotNone(trade.buy_trade_price)
            self.assertIsNotNone(trade.sell_trade_price)
            self.assertIsNotNone(trade.buy_book_price)
            self.assertIsNotNone(trade.sell_book_vol)
            self.assertIsNotNone(trade.sell_book_price)
            self.assertIsNotNone(trade.buy_book_vol)
            self.assertIsNotNone(trade.market_sell_price)
            self.assertIsNotNone(trade.buy_trade_vol)
            self.assertIsNotNone(trade.fix_buy_price)
            self.assertIsNotNone(trade.market_buy_price)
            self.assertIsNotNone(trade.time)

            print(trade.time)

            num_of_records += 1

        print(num_of_records)


if __name__ == '__main__':
    unittest.main()
