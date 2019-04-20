import gym
import numpy as np

from log.constant import *


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
    def __init__(self):
        super().__init__()

        self.action_space = gym.spaces.Discrete(5) #5 actions nop, buy, BUY, sell, SELL
        self.done = False

        self.board = np.ndarray(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH,  BOARD_WIDTH)


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

    #def _seed(self, seed=None):

