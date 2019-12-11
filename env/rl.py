from random import random
from glob import glob
import gym
import numpy as np
from log.constant import *
from log.dbgen import Generator

ONE_ORDER_SIZE = 1.0
MAX_DRAW_DOWN = 10
TIME_STEP_REWARD = -0.0000001

class TradeEnv(gym.Env):
    """The main OpenAI Gym class. It encapsulates an environment with
    arbitrary behind-the-scenes dynamics. An environment can be
    partially or fully observed.

    The main API methods that users of this class need to know are:

        step
        reset
        render
        close
        seed

    And set the following attributes:

        action_space: The Space object corresponding to valid actions
        observation_space: The Space object corresponding to valid observations
        reward_range: A tuple corresponding to the min and max possible rewards

    Note: a default reward range set to [-inf,+inf] already exists. Set it if you want a narrower range.

    The methods are accessed publicly as "step", "reset", etc.. The
    non-underscored versions are wrapper methods to which we may add
    functionality over time.
    """
    def __init__(self):
        super().__init__()

        # init members
        self.episode_done = None
        self.db_path = '/bitlog/bitlog.db'
        self.generator = Generator()
        self.board_generator = None
        self.board = None
        self.margin = 0

        self.action = ACTION.NOP

        self.sell_order_price = None
        self.buy_order_price = None

        self.sell_order = np.zeros((TIME_WIDTH, BOARD_WIDTH))
        self.buy_order = np.zeros((TIME_WIDTH, BOARD_WIDTH))

        # init gym environment
        self.action_space = gym.spaces.Discrete(5)   # 5 actions nop, buy, BUY, sell, SELL
        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=(6, TIME_WIDTH, BOARD_WIDTH),
            dtype=np.uint8
        )
        # self.reward_range = [-255., 255.]

        self.reset()

    def reset(self):
        self.new_episode()
        return self._observe()

    def step(self, action):
        '''
        :param action:
        :return: obvervation, reward, done, text
        '''
        self.new_sec()
        if not self.board:
            return None, 0, True, {}

        exec_time = False
        reward = 0
        text = {}

        if self.check_draw_down():
            # force to sell or buy now!!
            exec_time = 60
        elif action == ACTION.NOP:
            exec_time = self.action_nop()
            reward = TIME_STEP_REWARD
        elif action == ACTION.BUY:
            exec_time = self.action_buy()
            if not exec_time:
                reward = TIME_STEP_REWARD
        elif action == ACTION.BUY_NOW:
            exec_time = self.action_buy_now()
            if not exec_time:
                reward = TIME_STEP_REWARD
        elif action == ACTION.SELL:
            exec_time = self.action_sell()
            if not exec_time:
                reward = TIME_STEP_REWARD
        elif action == ACTION.SELL_NOW:
            exec_time = self.action_sell_now()
            if not exec_time:
                reward = TIME_STEP_REWARD
        else:
            print('Unknown action no->', action)

        self.evaluate()
        self.action = action
        if self.episode_done:
            reward = self.margin

        observation = self._observe()
        self.skip_sec(exec_time - 1)

        return observation, reward, self.episode_done, text

    def render(self, mode='human', close=False):
        pass

    def _observe(self):
        if self.board:
            '''
            #    return np.stack([self.board.buy_order.get_board(), self.board.sell_order.get_board(),
            #                    self.board.buy_trade.get_board(), self.board.sell_trade.get_board(),
            #                   self.sell_order, self.buy_order])
            '''
            a, b, c, d = self.board.get_std_boards()
            return np.stack([a, b, c, d, self.sell_order, self.buy_order])

        else:
            print("ERROR in _observe")
            # todo: fix size
            return np.zeros((6, TIME_WIDTH, BOARD_WIDTH))

    def new_episode(self):
        '''
        reset environment with new episode
        :return:
        '''
        self.sell_order_price = None
        self.buy_order_price = None
        self.margin = 0

        self.board_generator = self.generator.create(db_name=self.db_path)
        self.episode_done = False
        self.new_sec()

    def new_sec(self):
        self.board = next(self.board_generator, None)
        if self.board is None:
            self.episode_done = True

        return self.board

    def skip_sec(self, sec):
        board = None
        for _ in range(sec):
            board = self.new_sec()
            if not board:
                break
        return board

    def check_draw_down(self):
        if self.sell_order_price and self.sell_order_price - self.board.buy_book_price < (- MAX_DRAW_DOWN):
            print("SELL DRAW DOWN")
            return self.action_buy_now()

        elif self.buy_order_price and self.board.sell_book_price - self.buy_order_price < (- MAX_DRAW_DOWN):
            print("BUY DRAW DOWN")
            return self.action_sell_now()

        return False

    def action_nop(self):
        return 1

    def action_sell(self):
        if self.sell_order_price:  # sell order exist(cannot sell twice at one time)
            return 1

        price = self.board.fix_sell_price

        if price:
            self.sell_order_price = price
            print('ACTION:sell', self.sell_order_price)
            return self.board.fix_sell_price_time - self.board.current_time + 30

        print('ACTION:sell skip 300 sec')
        return 300

    def action_buy(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return 1

        price = self.board.fix_buy_price

        if price:
            self.buy_order_price = price
            print('ACTION:buy', self.buy_order_price)
            return self.board.fix_buy_price_time - self.board.current_time + 30

        print('ACTION:buy skip 300 sec')
        return 300

    def action_sell_now(self):
        if self.sell_order_price: # sell order exist(cannot sell twice at one time)
            return 1

        price = self.board.sell_book_price

        if price:
            self.sell_order_price = price
            print('ACTION:sell now', self.sell_order_price)
            return 30
        return 60

    def action_buy_now(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return 1

        price = self.board.buy_book_price

        if price:
            self.buy_order_price = price
            print('ACTION:buy now', self.buy_order_price)
            return 30
        return 60

    def evaluate(self):
        if self.buy_order_price and self.sell_order_price:
            self.margin = self.sell_order_price - self.buy_order_price
            self.episode_done = True
            print('epsode done->', self.board.current_time, 'margin->', self.margin)

        elif self.buy_order_price:
            self.margin = self.board.sell_book_price - self.buy_order_price
        elif self.sell_order_price:
            self.margin = self.sell_order_price - self.board.buy_book_price
        else:
            self.margin = 0

