import gym

class Trade(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = gym.spaces.Discrete(5) #buy(2), sell(2), nop

    def _step(self, action):
        pass

    def _rest(self):
        pass

    def _render(self, mode='human', close=False):
        pass

    def _seed(self, seed=None):
        pass

