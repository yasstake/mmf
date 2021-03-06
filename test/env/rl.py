import unittest
from env.rl import TradeEnv
from log.constant import ACTION

import numpy as np

class MyTestCase(unittest.TestCase):
    def test_create(self):
        env = TradeEnv()
        self.assertTrue(env is not None)

    def test_reset(self):
        env = TradeEnv()
        env.reset()

    def test_step(self):
        env = TradeEnv()
        env.step(1)

    def test_render(self):
        env = TradeEnv()
        env.render()

    def test_close(self):
        env = TradeEnv()
        env.close()

    def test_seed(self):
        env = TradeEnv()
        env.seed()

    def test_new_episode(self):
        env = TradeEnv()
        env.new_episode()

    def test_generator(self):
        env = TradeEnv()
        board = env.new_sec()
        print(board.current_time)
        print(board.q_value)
        board = env.new_sec()
        print(board.q_value)
        print(board.current_time)
        board = env.new_sec()
        print(board.q_value)
        print(board.current_time)

    def test_action1(self):
        env = TradeEnv()
        print(env.board.current_time)
        print(env.q_value)
        env.step(ACTION.NOP)

        print(env.board.current_time)
        print(env.q_value)
        env.step(ACTION.SELL_NOW)

        print(env.board.current_time)
        print(env.q_value)
        env.step(ACTION.BUY_NOW)



    def test_action2(self):
        env = TradeEnv()
        env.step(ACTION.SELL)
        env.step(ACTION.BUY)

    def test_action_sell(self):
        env = TradeEnv()

        env.step(ACTION.SELL)

        print('1')

        env.step(ACTION.BUY)

        print('2')
        env.step(ACTION.SELL)

        print('3')
        env.step(ACTION.BUY)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)
        env.step(ACTION.SELL)


    def test_buy(self):
        env = TradeEnv()
        env.action_buy()

    def test_sell(self):
        env = TradeEnv()
        env.action_sell()

    def test_buy_now(self):
        env = TradeEnv()
        env.action_buy_now()

    def test_sell_now(self):
        env = TradeEnv()
        env.action_sell_now()

    def test_ones(self):
        print(X)
        print(O)

#        A = np.zeros((TIME_WIDTH, BOARD_WIDTH))
        A_1 = np.stack([X, O, O, O, O, O, O])


        print(A_1)

if __name__ == '__main__':
    unittest.main()
