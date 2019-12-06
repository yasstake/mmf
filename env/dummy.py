import gym
import numpy as np




class DummyTrade(gym.Env):
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

        self.BOARD = np.array([
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]],

            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]],

            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]
        ])

        self.action_space = gym.spaces.Discrete(5)   # 5 actions nop, buy, BUY, sell, SELL
        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=self.BOARD.shape,
            dtype=np.uint8
        )

        # self.reward_range = [-255., 255.]

        self.reset()

    def reset(self):
        return self.BOARD.copy()

    def step(self, action):
        '''
        :param action:
        :return: obvervation, reward, done, text
        '''
        return self._observe(), 0, False, {}

    def render(self, mode='human', close=False):
        pass

    def _observe(self):
        return self.BOARD.copy()

