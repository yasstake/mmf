import glob
import random

import gym
import numpy as np
import tensorflow as tf

from dl.tfrecords import read_tfrecord_example
from log.constant import *

EPISODE_FRAMES = 3600 * 4
EPISODE_FILES  = int(EPISODE_FRAMES / BOARD_IN_FILE)

ONE_ORDER_SIZE = 1.0
MAX_DRAW_DOWN  = 6


class Observation:
    def __init__(self, env):
        # self.board = tf.reshape(env.boards, [-1, NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH])
        self.board = tf.reshape(env.boards, [NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH])
        self.board = self.board.numpy().astype(float) / 255.0
        self.rewards = None
        self.action = env.action

        self.sell_book_price = env.sell_book_price
        self.sell_book_vol = env.sell_book_vol
        self.buy_book_price = env.buy_book_price
        self.buy_book_vol = env.buy_book_vol

        self.sell_order_price = env.sell_order_price
        self.buy_order_price = env.buy_order_price

        self.margin = env.margin

        self.sell_now_reward = None
        self.buy_now_reward = None

        self.time = env.time

        self.buy_reward_flag = 0
        self.buy_reward = 0
        self.sell_reward_flag = 0
        self.sell_reward = 0

        if env.sell_order_price:
            pos = self.calc_order_pos(env.sell_order_price, env)
            self.board[LAYER_BUY_BOOK][0][pos] = 1.0
            self.board[LAYER_BUY_TRADE][0][pos] = 1.0

            self.sell_reward_flag = 1
            self.sell_reward = env.sell_order_price - env.buy_book_price

            # lets buy
            if env.sell_order_price < self.buy_book_vol:  # < 1BTC
                price = self.buy_book_price
            else:
                price = self.buy_book_price + PRICE_UNIT

            price = price * TAKER_BUY
            self.buy_now_reward = env.sell_order_price - price

        if env.buy_order_price:
            pos = self.calc_order_pos(env.buy_order_price, env)
            self.board[LAYER_SELL_BOOK][0][pos] = 1.0
            self.board[LAYER_SELL_TRADE][0][pos] = 1.0

            self.buy_reward_flag = 1
            self.buy_reward = env.sell_book_price - env.buy_order_price

            # lets sell
            if env.buy_order_price < self.sell_book_vol:  # < 1BTC
                price = self.sell_book_price
            else:
                price = self.sell_book_price - PRICE_UNIT

            price = price * TAKER_SELL
            self.sell_now_reward = price - env.buy_order_price

        self.rewards = np.array([self.sell_reward, self.sell_reward_flag, self.buy_reward, self.buy_reward_flag])

    def to_string(self):
        s = str(self.time)
        s += str(self.buy_order_price) + ' '
        s += str(self.sell_order_price)

        return s

    def is_able_to_sell(self):
        if self.sell_order_price:
            return False
        return True

    def get_sell_now_reward(self):
        return self.sell_now_reward

    def is_able_to_buy(self):
        if self.buy_order_price:
            return False
        return True

    def get_buy_now_reward(self):
        return self.buy_now_reward

    def calc_order_pos(self, price, env):
        pos = int((price - env.center_price) / PRICE_UNIT + BOARD_WIDTH/2)

        if pos < 0:
            pos = 0
        elif BOARD_WIDTH <= pos:
            pos = BOARD_WIDTH - 1

        return pos

class Episode:
    episode = 0
    total_reward = 0

class Trade(gym.Env):
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

    data_file_sets = None

    def __init__(self, data_pattern=DEFAULT_TF_DATA_DIR + '/**/*.tfrecords'):
        super().__init__()

        self.action_space = gym.spaces.Discrete(5) #5 actions nop, buy, BUY, sell, SELL

        self.data_path = data_pattern
        self.dataset = None

        self.data_files = self.list_tfdata_list(data_pattern)
        self.number_of_files = len(self.data_files)

        if Trade.data_file_sets is None:
            Trade.data_file_sets= []
            for file in self.data_files:
                Trade.data_file_sets += tf.data.Dataset.list_files(file).cache()

        self.action = None

        self.boards = None
        self.sell_book_price = None
        self.sell_book_vol = None
        self.buy_book_price = None
        self.buy_book_vol = None
        self.center_price = None
        self.sell_trade_price = None
        self.sell_trade_vol = None
        self.buy_trade_price = None
        self.buy_trade_vol = None
        self.market_buy_price = None
        self.market_sell_price = None
        self.fix_buy_price = None
        self.fix_sell_price = None
        self.time = None
        self.episode_done = False

        self.sell_order_price = 0
        self.buy_order_price = 0
        self.margin = 0

        self.new_generator = None

    def reset(self):
        return self.new_episode()

    def step(self, action):

        observe = None
        reward = 0
        text = {}

        result = False

        if not self.new_sec():
            if self.sell_order_price:
                action = ACTION.BUY_NOW
                result = self.action_buy_now()
            elif self.buy_order_price:
                action = ACTION.SELL_NOW
                result = self.action_sell_now()
        elif self.check_draw_down():
            result = True
        elif action == ACTION.NOP:
            result = self.action_nop()
            reward = -0.0000001
        elif action == ACTION.BUY:
            result = self.action_buy()
            if not result:
                reward = -0.00001
        elif action == ACTION.BUY_NOW:
            result = self.action_buy_now()
            if not result:
                reward = -0.00001
        elif action == ACTION.SELL:
            result = self.action_sell()
            if not result:
                reward = -0.00001
        elif action == ACTION.SELL_NOW:
            result = self.action_sell_now()
            if not result:
                reward = -0.00001
        else:
            print('Unknown action no->', action)

        if result:
            self.action = action
        else:
            print("NOP", action)
            self.action = ACTION.NOP

        self.evaluate()

        if self.episode_done:
            reward = self._calc_reward()

        observe = Observation(self)

        return observe, reward, self.episode_done, text

    def _calc_reward(self):

        reward = self.margin

        Episode.episode += 1
        Episode.total_reward += reward
        self.logger.log_reward(Episode.episode, reward, Episode.total_reward)
        print('reward->', reward)

        return reward

    def render(self, mode='human', close=False):
        pass

    def new_sec(self):
        data_available = False
        try:
            data_available = next(self.new_generator)
        except:
            pass

        if data_available:
            self.episode_done = False
        else:
            self.episode_done = True

        return data_available

    def new_sec_generator(self):
        for rec in self.dataset:
            self.decode_dataset(rec)

            yield True
        yield False

    def skip_sec(self, sec):
        while sec:
            rec_available = self.new_sec()

            if not rec_available:
                return False
            sec -= 1

        return True


    def list_tfdata_list(self, data_pattern=DEFAULT_TF_DATA_DIR + '/**/*.tfrecords'):
        '''
        List and ordered data file list
        each file contains as much as 600 boards
        :param data_pattern:
        :return: board list(acc ordered in time frame)
        '''

        files = sorted(glob.glob(data_pattern, recursive=True))


        return files


    def _new_file_index(self):
        '''
        calc start frame randomly
        '''
        if EPISODE_FILES < self.number_of_files:
            margin_rate = self.number_of_files - EPISODE_FILES
        else:
            print("Not enough frames")
            margin_rate = self.number_of_files

        new_index = int(random.random() * margin_rate)

        return new_index

    def _skip_count(self):
        return int(random.random() * (BOARD_IN_FILE*0.95))

    def _new_episode_files(self):
        start = self._new_file_index()
        end = start + EPISODE_FILES + 1

        files = self.data_files[start:end]

        return files

    def new_episode(self) -> Observation:
        start = self._new_file_index()
        end = start + EPISODE_FILES + 1
        skip = self._skip_count()

        return self._new_episode(start, end, skip)

    def _new_episode(self, start, end, skip = 0)->Observation:
        data = Trade.data_file_sets[start:end]
        dataset = tf.data.TFRecordDataset(data, compression_type='GZIP')
        self.dataset = dataset.map(read_tfrecord_example)

        self.new_generator = self.new_sec_generator()

        if skip:
            self.skip_sec(skip)

        self.sell_order_price = 0
        self.buy_order_price = 0

        return Observation(self)


    def decode_dataset(self, data):

        self.boards = tf.io.decode_raw(data['board'], tf.uint8)
        #self.board = tf.reshape(boards, [-1, NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH])

        self.center_price = data['center_price']
        self.sell_book_price = data['sell_book_price']
        self.sell_book_vol = data['sell_book_vol']
        self.buy_book_price = data['buy_book_price']
        self.buy_book_vol = data['buy_book_vol']
        self.sell_trade_price = data['sell_trade_price']
        self.sell_trade_vol = data['sell_trade_vol']
        self.buy_trade_price = data['buy_trade_price']
        self.buy_trade_vol = data['buy_trade_vol']
        self.market_buy_price = data['market_buy_price']
        self.market_sell_price = data['market_sell_price']
        self.fix_buy_price = data['fix_buy_price']
        self.fix_sell_price = data['fix_sell_price']
        self.time  = data['time']

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

        order_price = self.sell_book_price
        volume = order_price * ONE_ORDER_SIZE
        volume += self.sell_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec() and time_count:
            if order_price <= self.buy_trade_price:
                volume -= self.buy_trade_vol

            if self.sell_book_price < order_price:
                self.skip_sec(60)
                return False

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

        order_price = self.buy_book_price
        volume = order_price * ONE_ORDER_SIZE
        volume += self.buy_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec() and time_count:
            if self.sell_trade_price <= order_price:
                volume -= self.sell_trade_vol

            if order_price < self.buy_book_price:
                self.skip_sec(60)
                return False

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

        volume = self.buy_book_price * ONE_ORDER_SIZE

        if volume < self.buy_book_vol:
            self.sell_order_price = volume * TAKER_SELL
        else:
            self.sell_order_price = (volume - PRICE_UNIT) * TAKER_SELL

        print('ACTION:sell now', self.sell_order_price)

        return True

    def action_buy_now(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return False

        volume = self.sell_book_price * ONE_ORDER_SIZE

        if volume < self.sell_book_vol:
            self.buy_order_price = volume * TAKER_BUY
        else:
            self.buy_order_price = (volume + PRICE_UNIT) * TAKER_BUY

        print('ACTION:buy now', self.buy_order_price)

        return True

    def evaluate(self):
        if self.buy_order_price and self.sell_order_price:
            self.margin = self.sell_order_price - self.buy_order_price
            self.sell_order_price = 0
            self.buy_order_price = 0
            self.episode_done = True
        elif self.buy_order_price:
            self.margin = self.sell_book_price - self.buy_order_price
        elif self.sell_order_price:
            self.margin = self.sell_order_price - self.buy_book_price
        else:
            self.margin = 0
