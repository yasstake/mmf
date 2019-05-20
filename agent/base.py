import random

import numpy as np
import tensorflow as tf

from env.trade import Trade
from log.constant import ACTION

tf.enable_v2_behavior()

class BaseAgent:
    def __init__(self, epsilon=0.0005):
        self.epsilon = epsilon
        self.estimate_probs = False
        self.actions = [ACTION.NOP, ACTION.SELL, ACTION.SELL_NOW, ACTION.BUY, ACTION.BUY_NOW]
        self.number_of_actions = len(self.actions)
        self.initialized = False

    def play(self, env: Trade, no_of_episode: int):
        total_reward = 0

        while no_of_episode:
            total_reward += self.one_episode(env)
            no_of_episode -= 1

        print('TOTAL rewards->', total_reward)

    def one_episode(self, env: Trade):
        s = env.new_episode()

        while True:
            action = self.policy(s)
            print('action->', action, end='')
            next_state, reward, done, info = env.step(action)
            print('reward->', reward)
            if done:
                break
            s = next_state

        return reward

    def set_initialized(self):
        self.initialized = True

    def policy(self, s):
        if np.random.random() < self.epsilon or not self.initialized:
            return self.random_action()
        else:
            estimates = self.estimate(s)

            if self.estimate_probs:
                print('random')
                action = np.random.choice(self.actions, size=1, p=estimates)[0]
            else:
                action = np.argmax(estimates)
                if estimates[action] <= 0:
                    action = ACTION.NOP

            print('{:8f} {: 4.5f} {: 4.5f} {: 4.5f} {: 4.5f} {: 4.5f}   a{:1}  BP {: 5.1f}   SP {: 5.1f} / bp {: 5.1f} sp {: 5.1f}, m {: 5.1f}'
                  .format(s.time, estimates[0], estimates[1], estimates[2], estimates[3], estimates[4],
                          action, s.buy_order_price, s.sell_oder_price, s.buy_book_price, s.sell_book_price, s.margin))

            return action

    def estimate(self, s):
        return np.random.random(), np.random.random(), np.random.random(), np.random.random(), np.random.random()

    def random_action(self):
        action = random.choice(self.actions)

        return action

    def update(self, experiences, gamma):
        pass

    def update_model(self):
        pass

    def episode_begin(self, i, trainer):
        pass

    def episode_end(self, i, trainer):
        pass

if __name__ == '__main__':
    env = Trade()
    agent = BaseAgent()
    agent.play(env, 100)


