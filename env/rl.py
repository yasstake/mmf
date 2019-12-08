from random import random
from glob import glob
import gym
import numpy as np
from log.constant import *
from log.dbgen import Generator

EPISODE_FRAMES = 3600 * 2   # 2Hour
EPISODE_FILES = int(EPISODE_FRAMES / BOARD_IN_FILE)

ONE_ORDER_SIZE = 1.0
MAX_DRAW_DOWN = 6
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
        self.board_generator = None
        self.board = None
        self.margin = 0

        self.sell_order_price = None
        self.buy_order_price = None

        # init gym environment
        self.action_space = gym.spaces.Discrete(5)   # 5 actions nop, buy, BUY, sell, SELL
        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=(32, 600, 4), # todo: fix size
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

        return self._observe(), 0, self.episode_done, {}

    def render(self, mode='human', close=False):
        pass

    def _observe(self):
        if self.board:
            return self.board.get_board()
        else:
            return None

    def new_episode(self):
        '''
        reset environment with new episode
        :return:
        '''
        self.sell_order_price = None
        self.buy_order_price = None
        self.margin = 0

        self.board_generator = Generator.create(db_name=self.db_path)
        self.episode_done = False
        self.new_sec()

    def new_sec(self):
        self.board = next(self.board_generator)
        if self.board is None:
            self.episode_done = True
        return self.board

    def skip_sec(self, sec):
        for _ in range(sec):
            board = self.new_sec()
            if not board:
                return None
        return board

    def check_draw_down(self):
        if self.sell_order_price and self.sell_order_price - self.buy_book_price < (- MAX_DRAW_DOWN):
            print("SELL DRAW DOWN")
            return self.action_buy_now()

        elif self.buy_order_price and self.sell_book_price - self.buy_order_price < (- MAX_DRAW_DOWN):
            print("BUY DRAW DOWN")
            return self.action_sell_now()

        return False

    def action_nop(self):
        return True

    def action_sell(self):
        if self.sell_order_price:  # sell order exist(cannot sell twice at one time)
            return False

        order_price = self.board.sell_book_price
        volume = order_price * ONE_ORDER_SIZE
        volume += self.board.sell_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec() and time_count:
            if order_price <= self.board.buy_trade_price:
                volume -= self.board.buy_trade_volume

            '''
            # fail to sell(order book is moving to another side)
            if self.board.sell_book_price < order_price:
                self.skip_sec(60)
                return False
            '''
            if volume <= 0:
                self.sell_order_price = order_price * MAKER_SELL
                break

            time_count -= 1

        if time_count <= 0:
            return False

        print('ACTION:sell', self.sell_order_price)
        return True

    def action_buy(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return False

        order_price = self.board.buy_book_price
        volume = order_price * ONE_ORDER_SIZE
        volume += self.board.buy_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec() and time_count:
            if self.board.sell_trade_price <= order_price:
                volume -= self.board.sell_trade_volume

            '''
            # fail to buy, board is moving to another side
            if order_price < self.board.buy_book_price:
                self.skip_sec(60)
                return False
            '''
            if volume <= 0:
                self.buy_order_price = order_price * MAKER_BUY
                break

            time_count -= 1

        if time_count <= 0:
            return False

        print('ACTION:buy', self.buy_order_price)

        return True

    def action_sell_now(self):
        if self.sell_order_price: # sell order exist(cannot sell twice at one time)
            return False

        volume = self.board.buy_book_price * ONE_ORDER_SIZE

        if volume < self.board.buy_book_vol:
            self.sell_order_price = volume * TAKER_SELL
        else:
            self.sell_order_price = (volume - PRICE_UNIT) * TAKER_SELL

        print('ACTION:sell now', self.sell_order_price)

        return True

    def action_buy_now(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return False

        volume = self.board.sell_book_price * ONE_ORDER_SIZE

        if volume < self.board.sell_book_vol:
            self.buy_order_price = volume * TAKER_BUY
        else:
            self.buy_order_price = (volume + PRICE_UNIT) * TAKER_BUY

        print('ACTION:buy now', self.buy_order_price)

        return True

    def evaluate(self):
        if self.buy_order_price and self.sell_order_price:
            self.margin = self.sell_order_price - self.buy_order_price
            self.episode_done = True
        elif self.buy_order_price:
            self.margin = self.board.sell_book_price - self.buy_order_price
        elif self.sell_order_price:
            self.margin = self.sell_order_price - self.board.buy_book_price
        else:
            self.margin = 0

