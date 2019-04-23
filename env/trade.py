import glob
import random

import gym
import numpy as np
import tensorflow as tf

from dl.tfrecords import read_tfrecord
from log.constant import *

EPISODE_FRAMES = 3600 * 3
EPISODE_FILES  = int(EPISODE_FRAMES / BOARD_IN_FILE)

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

        self.board = np.ndarray((NUMBER_OF_LAYERS, BOARD_TIME_WIDTH,  BOARD_WIDTH))
        self.data_path = data_pattern

        self.data_files = self.list_tfdata_list(data_pattern)
        self.number_of_files = len(self.data_files)



    def _reset(self):
        pass

    def _step(self, action):

        reward = 0


         # buy

         # buy2

         # Sell

         # Sell2

         # Nop


         # retrun (xxxxxx,xxxx,xxxx,xxxx)
        return self.board, reward, self.done, {}

    def _render(self, mode='human', close=False):
        pass


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
        return int(random.random() * BOARD_IN_FILE)


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

        print(episode_files)

        dataset = tf.data.Dataset.list_files(episode_files)
        dataset = tf.data.TFRecordDataset(dataset, compression_type='GZIP')
        dataset = dataset.map(read_tfrecord)

        return dataset


    def action_nop(self):
        pass

    def action_sell(self):
        pass

    def action_sell_now(self):
        pass

    def action_buy(self):
        pass

    def action_buy_now(self):
        pass
