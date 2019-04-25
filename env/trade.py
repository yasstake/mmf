import glob
import random

import gym
import tensorflow as tf

from dl.tfrecords import read_tfrecord_example
from log.constant import *

EPISODE_FRAMES = 3600 * 3
EPISODE_FILES  = int(EPISODE_FRAMES / BOARD_IN_FILE)

ONE_ORDER_SIZE = 1.0


class Observation:
    def __init__(self, env):
        self.board = env.board
        self.sell_order_price = env.sell_order_price
        self.buy_order_price = env.buy_order_price
        self.margin = env.margin


class Trade(gym.Env):
    '''
    When implementing an environment, override the following methods
    in your subclass:
        _step
        _reset
        _render
        _close
        _configure
        _seed
    And set the following attributes:
        action_space: The Space object corresponding to valid actions
        observation_space: The Space object corresponding to valid observations
        reward_range: A tuple corresponding to the min and max possible rewards

    '''
    def __init__(self, data_pattern=DEFAULT_TF_DATA_DIR + '/**/*.tfrecords'):
        super().__init__()

        self.action_space = gym.spaces.Discrete(5) #5 actions nop, buy, BUY, sell, SELL
        self.done = False

        self.data_path = data_pattern

        self.data_files = self.list_tfdata_list(data_pattern)
        self.number_of_files = len(self.data_files)

        self.dataset = None

        self.board = None
        self.sell_book_price = None
        self.sell_book_vol = None
        self.buy_book_price = None
        self.buy_book_vol = None
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



    def _reset(self):
        self.new_episode()


    def _step(self, action):

        observe = None
        reward = 0
        text = {}

        self.new_sec()

        result = False
        if action == ACTION.NOP:
            result = self.action_nop()
        elif action == ACTION.BUY:
            result = self.action_buy()
        elif action == ACTION.BUY_NOW:
            result = self.action_buy_now()
        elif action == ACTION.SELL:
            result = self.action_sell()
        elif action == ACTION.SELL_NOW:
            result = self.action_sell_now()
        else:
            print('Unknown action no->', action)

        self.evaluate()
        observe = Observation(self)

        if result:
            reward = self._calc_reward()
        else:
            reward = 0

        return observe, reward, self.episode_done, text


    def _calc_reward(self):
        return self.margin

    def _render(self, mode='human', close=False):
        pass


    def new_sec(self):
        data_available = next(self.new_generator)

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

        files = glob.glob(data_pattern, recursive=True)
        return sorted(files)

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


    def new_episode(self):
        '''
        reset randomly stat point of the sequence
        :return: new dataset for one episode
        '''
        episode_files = self._new_episode_files()

        dataset = tf.data.Dataset.list_files(episode_files)
        dataset = tf.data.TFRecordDataset(dataset, compression_type='GZIP')
        self.dataset = dataset.map(read_tfrecord_example)

        self.new_generator = self.new_sec_generator()

        self.skip_sec(self._skip_count())

        self.sell_order_price = 0
        self.buy_order_price = 0




    def decode_dataset(self, data):

        boards = tf.io.decode_raw(data['board'], tf.uint8)
        self.board = tf.reshape(boards, [-1, NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH])

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

    def action_nop(self):
        return False

    def action_sell(self):
        if self.sell_order_price:  # sell order exist(cannot sell twice at one time)
            return False

        self.new_sec()

        volume = self.sell_book_price * ONE_ORDER_SIZE
        order_price = volume * MAKER_SELL
        volume += self.sell_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec():
            if self.buy_trade_price <= self.sell_book_price:
                volume -= self.buy_trade_vol

            if volume <= 0:
                self.sell_order_price = order_price
                break

            if time_count <= 0:
                break
            time_count -= 1

        if time_count <= 0:
            return False

        return True


    def action_sell_now(self):
        if self.sell_order_price: # sell order exist(cannot sell twice at one time)
            return False

        self.new_sec()
        volume = self.buy_book_price * ONE_ORDER_SIZE

        if volume < self.buy_book_vol:
            self.sell_order_price = volume * TAKER_SELL
        else:
            self.sell_order_price = (volume - PRICE_UNIT) * TAKER_SELL

        return True


    def action_buy(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return False

        self.new_sec()

        order_price = self.buy_book_price
        volume = order_price * ONE_ORDER_SIZE
        volume += self.buy_book_vol

        time_count = TRAN_TIMEOUT

        while self.new_sec() and time_count:
            if self.sell_trade_price <= order_price:
                volume -= self.sell_trade_vol

            if volume <= 0:
                self.buy_order_price = order_price * MAKER_BUY
                break

            time_count -= 1

        if time_count <= 0:
            return False

        return True


    def action_buy_now(self):
        if self.buy_order_price: # buy order exist(cannot sell twice at one time)
            return False

        self.new_sec()
        volume = self.sell_book_price * ONE_ORDER_SIZE

        if volume < self.sell_book_vol:
            self.buy_order_price = volume * TAKER_BUY
        else:
            self.buy_order_price = (volume + PRICE_UNIT) * TAKER_BUY

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
            pass
