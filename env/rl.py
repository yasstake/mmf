from random import random
from glob import glob
import gym
import numpy as np
import tensorflow as tf
from log.constant import *
from dl.tfrecords import read_tfrecord_example

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

        self.board = np.zeros((32, 600, 6), dtype=np.uint8)

        self.action_space = gym.spaces.Discrete(5)   # 5 actions nop, buy, BUY, sell, SELL
        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=self.board.shape,
            dtype=np.uint8
        )
        # self.reward_range = [-255., 255.]

        self.board_generator = None

        self.data_path = DEFAULT_TF_DATA_DIR + '/**/*.tfrecords'
        self.data_files = self._list_tfdata(self.data_path)
        self.number_of_files = len(self.data_files)

        self.episode_files = None

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
        self.reset()

    def reset(self):
        self.new_episode()
        return self._observe()

    def step(self, action):
        '''
        :param action:
        :return: obvervation, reward, done, text
        '''
        return self._observe(), 0, self.episode_done, {}

    def render(self, mode='human', close=False):
        pass

    def _observe(self):
        return self.board.copy()

    def _list_tfdata(self, data_pattern=DEFAULT_TF_DATA_DIR + '/**/*.tfrecords'):
        '''
        List and ordered data file list
        each file contains as much as 600 boards
        :param data_pattern:
        :return: board list(acc ordered in time frame)
        '''
        files = sorted(glob(data_pattern, recursive=True))

        return files

    def _new_file_index(self):
        '''
        calc start frame randomly
        return:
        '''
        if EPISODE_FILES < self.number_of_files:
            start_file_index = self.number_of_files - EPISODE_FILES
        else:
            print("[WARN] Not enough data files")
            start_file_index = self.number_of_files

        new_index = int(start_file_index * random())

        return new_index

    def _skip_count(self):
        '''
        :return: number of skip frames in a data file
        '''
        return int((BOARD_IN_FILE*0.9) * random())

    def _new_episode_files(self):
        '''
        :return: set of new episode files
        '''
        start = self._new_file_index()
        end = start + EPISODE_FILES + 1
        if self.number_of_files < end:
            end = self.number_of_files

        files = self.data_files[start:end]

        return files

    def new_episode(self):
        '''
        reset environment with new episode
        :return:
        '''
        self.action = ACTION.NOP
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

        self.sell_order_price = None
        self.buy_order_price = None
        self.margin = None

        self.episode_files = self._new_episode_files()
        self._new_episode()

    def _new_episode(self, skip=True):
        '''
        :param skip: skip a few frames from a begining
        '''
        dataset = tf.data.TFRecordDataset(self.episode_files, compression_type='GZIP')
        self.dataset = dataset.map(read_tfrecord_example)

        self.new_generator = self.new_sec_generator()

        if skip:
            skip_time = self._skip_count()
            self.skip_sec(skip_time)

        self.episode_done = False
        self.sell_order_price = 0
        self.buy_order_price = 0

    def new_sec(self):
        data_available = next(self.new_generator)
        return data_available

    def skip_sec(self, skip_count):
        while skip_count:
            self.new_sec()
            skip_count -= 1

    def new_sec_generator(self):
        for rec in self.dataset:
            last_time = self.time
            self.decode_dataset(rec)

            if last_time and MAX_SKIP_TIME < self.time - last_time:
                break

            yield True
        yield False

    def decode_dataset(self, data):
        self.boards = tf.io.decode_raw(data['board'], tf.uint8)

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
        self.time = data['time']

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

