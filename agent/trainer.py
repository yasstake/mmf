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

            total_reward = 0
            while True:
                if render:
                    env.render()

                a = agent.policy(s)
                n_state, reward, done, info = env.step(a)
                #print('step->', a, 'reward->', reward)
                if done:
                    break

                total_reward += reward
                e = Experience(s, a, reward, n_state, done)
                self.experiences.append(e)

                if 500 < len(self.experiences):
                    agent.set_initialized()
                    self.experiences.popleft()
                    batch = random.sample(self.experiences, 32)

                    loss = agent.update(batch, gamma=0)

            print('reward->', total_reward)
            self.episode_end(i, agent)

    def episode_begin(self, i:int, agent:BaseAgent):
        print("-------------------Episode start---------------->", i)

    def episode_end(self, i:int, agent:BaseAgent):
        agent.update_model()
        print("<------------------Episode end-------------------", i)




if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = BaseAgent()

    trainer.train(env, agent, eposode=10)
