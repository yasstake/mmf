from random import random
from glob import glob
import gym
import numpy as np
from log.constant import ACTION
from log.constant import TIME_WIDTH
from log.constant import BOARD_WIDTH
from log.dbgen import Generator
from log.qvalue import QValue

ONE_ORDER_SIZE = 1.0
MAX_DRAW_DOWN = 50
TIME_STEP_REWARD = -0.0001
TIME_STEP_REWARD_WITH_ORDER = -0.001
INVALID_ACTION_REWARD = -0.1


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
        self.q_value = QValue()

        self.episode_text = ''

        self.action = ACTION.NOP
        self.start_action = ACTION.NOP
        self.start_time = None

        self.sell_order_price = None
        self.buy_order_price = None

        self.episode_start_time = 0

        # init gym environment
        self.action_space = gym.spaces.Discrete(5)   # 5 actions nop, buy, BUY, sell, SELL

        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=(TIME_WIDTH, BOARD_WIDTH, 6),
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
            if self.sell_order_price or self.buy_order_price:
                reward = TIME_STEP_REWARD_WITH_ORDER
            else:
                reward = TIME_STEP_REWARD
        elif action == ACTION.BUY:
            exec_time = self.action_buy()
            if not exec_time:
                reward = INVALID_ACTION_REWARD
        elif action == ACTION.BUY_NOW:
            exec_time = self.action_buy_now()
            if not exec_time:
                reward = INVALID_ACTION_REWARD
        elif action == ACTION.SELL:
            exec_time = self.action_sell()
            if not exec_time:
                reward = INVALID_ACTION_REWARD
        elif action == ACTION.SELL_NOW:
            exec_time = self.action_sell_now()
            if not exec_time:
                reward = INVALID_ACTION_REWARD
        else:
            print('Unknown action no->', action)

        self.evaluate()
        self.action = action
        if self.start_action == ACTION.NOP and action != ACTION.NOP:
            self.start_action = action
            self.start_time = self.board.current_time

        if self.start_action == ACTION.NOP:
            print('start_time(noaction)', self.start_time, self.start_action)
            self.q_value = self.generator.select_q(self.board.current_time, self.board.current_time, ACTION.NOP)
        else:
            print('start_time', self.board.current_time, self.start_time, self.start_action)
            self.q_value = self.generator.select_q(self.board.current_time, self.start_time, self.start_action)

        if self.episode_done:
            reward = self.margin

        observation = self._observe()

        if exec_time:
            self.skip_sec(exec_time)

        return observation, reward, self.episode_done, text

    def render(self, mode='human', close=False):
        pass

    def _observe(self):

        if self.board:
            sell_order = np.zeros((TIME_WIDTH, BOARD_WIDTH))
            buy_order = np.zeros((TIME_WIDTH, BOARD_WIDTH))

            if self.sell_order_price:
                offset = self.board.price_offset(self.sell_order_price) - 1
                sell_order[:, offset:offset+1] = 255

            if self.buy_order_price:
                offset = self.board.price_offset(self.buy_order_price) + 1
                buy_order[:, offset:offset+1] = 255

            a, b, c, d = self.board.get_std_boards()

            r = np.stack([a, b, c, d, sell_order, buy_order], axis=2)

            return r

        else:
            print("ERROR in _observe")
            return np.zeros((TIME_WIDTH, BOARD_WIDTH, 6))

    def new_episode(self):
        '''
        reset environment with new episode
        :return:
        '''
        self.sell_order_price = None
        self.buy_order_price = None
        self.margin = 0

        self.episode_text = ''

        self.board_generator = self.generator.create(db_name=self.db_path)
        self.episode_done = False
        self.new_sec()
        if self.board:
            self.episode_start_time = self.board.current_time

    def new_sec(self):
        self.board = next(self.board_generator, None)

        if self.board is None:
            self.episode_done = True

        return self.board

    def skip_sec(self, sec=1):
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
        return 0

    def action_sell(self):
        if self.sell_order_price:  # sell order exist(cannot sell twice at one time)
            return 0

        price = self.board.fix_sell_price

        if price:
            self.sell_order_price = price
            self.episode_text += 'sell {}　[{}]  '.format(self.sell_order_price, self.board.current_time)
            print('ACTION:sell', self.sell_order_price, '(', self.board.current_time, ')')
            return self.board.fix_sell_price_time - self.board.current_time + 30

        print('ACTION:sell skip 300 sec')
        return 300

    def action_buy(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return 0

        price = self.board.fix_buy_price

        if price:
            self.buy_order_price = price
            self.episode_text += 'buy {}　[{}]  '.format(self.buy_order_price, self.board.current_time)
            print('ACTION:buy', self.buy_order_price, '(', self.board.current_time, ')')
            return self.board.fix_buy_price_time - self.board.current_time + 30

        print('ACTION:buy skip 300 sec')
        return 300

    def action_sell_now(self):
        if self.sell_order_price: # sell order exist(cannot sell twice at one time)
            return 0

        price = self.board.market_sell_price

        if price:
            self.sell_order_price = price
            self.episode_text += 'SELL {}　[{}]  '.format(self.sell_order_price, self.board.current_time)
            print('ACTION:sell now', self.sell_order_price, '(', self.board.current_time, ')')
            return 60
        return 60

    def action_buy_now(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return 0

        price = self.board.market_buy_price

        if price:
            self.buy_order_price = price
            self.episode_text += 'BUY {}　[{}]  '.format(self.buy_order_price, self.board.current_time)
            print('ACTION:buy now', self.buy_order_price, '(', self.board.current_time, ')')
            return 60
        return 60

    def evaluate(self):
        if self.buy_order_price and self.sell_order_price:
            self.margin = self.sell_order_price - self.buy_order_price
            self.episode_done = True

            self.episode_text += ' [{}]{}'.format(self.board.current_time - self.episode_start_time, self.margin)
            print('epsode done->', self.board.current_time, self.episode_text)

        elif self.buy_order_price:
            self.margin = self.board.sell_book_price - self.buy_order_price
        elif self.sell_order_price:
            self.margin = self.sell_order_price - self.board.buy_book_price
        else:
            self.margin = 0


