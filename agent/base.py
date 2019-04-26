import random

import tensorflow as tf

from env.trade import Trade
from log.constant import ACTION

tf.enable_v2_behavior()

class BaseAgent:
    def __init__(self):
        pass


    def play(self, env: Trade, no_of_episode: int):

        while no_of_episode:
            self.one_episode(env)

            no_of_episode -= 1


    def one_episode(self, env: Trade):
        env.new_episode()

        while True:
            action = random.choice([ACTION.NOP, ACTION.SELL, ACTION.SELL_NOW, ACTION.BUY, ACTION.BUY_NOW])
            observation, reward, done, info = env.step(action)
            if done:
                print('reward->', reward)
                break

        return



if __name__ == '__main__':
    env = Trade()
    agent = BaseAgent()
    agent.play(env, 100)


