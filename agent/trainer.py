from collections import deque
from collections import namedtuple

from gym import Env

from agent.base import *

BUFFER_SIZE = 20000

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd'])

class Trainer():
    def __init__(self, buffer_size=BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.experiences = deque(maxlen=self.buffer_size)
        self.reward = 0
        self.start_time = 0
        self.end_time = 0
        self.loss = None
        self.total_reward = 0
        self.duration = 0
        #self.logger = Logger()

    def train(self, env: Env, agent, eposode=200, observe_interval=10, render=False, min_buffer_size=100):
        for i in range(eposode):
            s = env.reset()

            self.episode_begin(i, agent, s)

            self.reward = 0
            self.start_time = s.time

            while True:
                if render:
                    env.render()

                a = agent.policy(s)
                n_state, reward, done, info = env.step(a)
                self.reward += reward

                e = Experience(s, a, reward, n_state, done)
                self.experiences.append(e)

                if min_buffer_size < len(self.experiences):
                    agent.set_initialized()

                    batch = random.sample(self.experiences, 64)
                    self.loss = agent.update(batch, gamma=0.995)

                s = n_state

                if done:
                    if s:
                        self.end_time = s.time
                    break

            self.episode_end(i, agent, s)

    def episode_begin(self, i:int, agent:BaseAgent, s):
        pass

    def episode_end(self, i:int, agent:BaseAgent, s):
        self.duration = float(self.end_time) - float(self.start_time)
        self.total_reward += self.reward
        #        s = '<- EPISODE END ({:5d}) loss({: 4.6f}), reward({: 4.6f}) duration({: 4f}) total reward ({: 6f}) '.format(i, self.loss, self.reward, self.duration, self.total_reward)

        s = '<- EPISODE END ({:5d}) '.format(i)

        print("<-- EPISODE END-- ", end='')
        print(i, end='')
        print(' // loss->', self.loss, end='')
        print(' // reward->', self.reward, end='')
        print(' // total reward->', self.total_reward, end='')
        print(' // buffer len->', len(self.experiences))

        agent.update_model()

        '''
        self.logger.write(i, 'loss', self.loss)
        self.logger.write(i, 'reward', self.reward)
        self.logger.write(i, 'total reward', self.total_reward)
        '''



        

if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = BaseAgent()

    trainer.train(env, agent, eposode=10)
