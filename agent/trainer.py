from collections import deque
from collections import namedtuple

from gym import Env

from agent.base import *

BUFFER_SIZE = 2048

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd'])

class Trainer():
    def __init__(self, buffer_size=BUFFER_SIZE):
        self.experiences = None
        self.buffer_size = buffer_size

    def train(self, env: Env, agent, eposode=200, observe_interval=10, render=False):
        self.experiences = deque(maxlen=self.buffer_size)

        for i in range(eposode):
            self.episode_begin(i, agent)
            s = env.reset()

            done = False

            total_reward = 0
            while not done:
                if render:
                    env.render()

                a = agent.policy(s)
                n_state, reward, done, info = env.step(a)
                total_reward += reward

                e = Experience(s, a, reward, n_state, done)
                self.experiences.append(e)

                if 1000 < len(self.experiences):
                    self.experiences.popleft()
                    loss = agent.update(self.experiences, 0.05)
                    print('loss->', loss)

            print('reward->', total_reward)
            agent.update_model()
            self.episode_end(i, agent)

    def episode_begin(self, i:int, agent:BaseAgent):
        print("Episode start->", i)

    def episode_end(self, i:int, agent:BaseAgent):
        print("<-Episode end", i)



if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = BaseAgent()

    trainer.train(env, agent, eposode=10)
