from collections import deque
from collections import namedtuple

from gym import Env

from agent.base import *

BUFFER_SIZE = 20000

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd'])

class Trainer():
    def __init__(self, buffer_size=BUFFER_SIZE):
        self.experiences = None
        self.buffer_size = buffer_size
        self.reward = 0
        self.start_time = 0
        self.loss = None
        self.ave_sec_reward = 0
        self.duration = 0

    def train(self, env: Env, agent, eposode=200, observe_interval=10, render=False, min_buffer_size=100):
        self.experiences = deque(maxlen=self.buffer_size)

        for i in range(eposode):
            s = env.reset()
            self.episode_begin(i, agent, s)

            while True:
                if render:
                    env.render()

                a = agent.policy(s)
                n_state, reward, done, info = env.step(a)
                if done:
                    break

                e = Experience(s, a, reward, n_state, done)
                self.experiences.append(e)

                if min_buffer_size < len(self.experiences):
                    agent.set_initialized()
                    self.reward += reward
                    batch = random.sample(self.experiences, 64)
                    self.loss = agent.update(batch, gamma=0.95)

                s = n_state

            self.episode_end(i, agent, s)

    def episode_begin(self, i:int, agent:BaseAgent, s):
        self.start_time = s.time

    def episode_end(self, i:int, agent:BaseAgent, s):
        if self.loss is not None:
            self.duration += float(s.time) - float(self.start_time)
        if self.duration:
            sec_reward = self.reward / self.duration
        else:
            sec_reward = 0
        self.ave_sec_reward = (self.ave_sec_reward * 9 + sec_reward) / 10
        print("<----Episode end--", i, 'loss->', self.loss, 'reward->', self.reward, 'duration', self.duration, 'reward/sec', sec_reward,'/', self.ave_sec_reward, 'buffer', len(self.experiences))

        agent.update_model()
        

if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = BaseAgent()

    trainer.train(env, agent, eposode=10)
