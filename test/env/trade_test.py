import glob
import unittest

import tensorflow as tf

from env.trade import Trade
from log.constant import ACTION

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


    def test_env_step(self):
        trade = Trade()
        trade.new_episode()

        trade.step(ACTION.NOP)
        trade.step(ACTION.BUY)
        trade.step(ACTION.BUY_NOW)
        trade.step(ACTION.SELL)
        trade.step(ACTION.SELL_NOW)

    def test_env_buy(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.BUY)
        print(trade.time)


    def test_env_buy_sell(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.BUY_NOW)
        print(trade.time)
        print(trade.buy_order_price)
        print(trade.margin)

        # close transaction
        print(trade.time)
        trade.step(ACTION.SELL_NOW)
        print(trade.time)
        print(trade.margin)


    def test_env_sell_buy(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.SELL_NOW)
        print(trade.time)
        print(trade.sell_order_price)
        print(trade.margin)

        # close transaction
        print(trade.time)
        trade.step(ACTION.BUY_NOW)
        print(trade.time)
        print(trade.margin)

    def test_sell_order(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.SELL)
        print(trade.time)
        print(trade.sell_order_price)
        print(trade.margin)


    def test_sell_order_buy(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.SELL)
        print(trade.time)
        print(trade.sell_order_price)
        print(trade.margin)

        print(trade.time)
        trade.step(ACTION.BUY)
        print(trade.time)
        print(trade.margin)


    def test_buy_order(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.BUY)
        print(trade.time)
        print(trade.buy_order_price)
        print(trade.margin)

    def test_buy_order_sell(self):
        trade = Trade()
        trade.new_episode()

        print(trade.time)
        trade.step(ACTION.BUY)
        print(trade.time)
        print(trade.buy_order_price)
        print(trade.margin)


        print(trade.time)
        trade.step(ACTION.SELL)
        print(trade.time)
        print(trade.margin)

    def test_actions(self):
        trade = Trade()
        trade.new_episode()

        print(trade.action_space)





if __name__ == '__main__':
    unittest.main()
