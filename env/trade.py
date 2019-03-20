import gym



class Trade(gym.Env):
    A = 1

    def __init__(self):
        super().__init__()

        self.action_space = gym.spaces.Discrete(5) #buy(2), sell(2), nop

    def _step(self, action):

        observation = None
        reward = 0
         # buy

         # buy2

         # Sell

         # Sell2

         # Nop


         # retrun (xxxxxx,xxxx,xxxx,xxxx)
        return observation, reward, self.done, {}


    def _rest(self):
        pass

    def _render(self, mode='human', close=False):
        pass

    def _seed(self, seed=None):
        pass


