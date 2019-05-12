from collections import deque
from collections import namedtuple

from agent.deepq import *
from env.log import Logger

BUFFER_SIZE = 20000

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd'])

class Trainer():
    def __init__(self, env, agent, gamma=0.99, buffer_size=BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.experiences = deque(maxlen=self.buffer_size)
        self.reward = 0
        self.start_time = 0
        self.end_time = 0
        self.loss = None
        self.total_reward = 0
        self.duration = 0
        self.logger = Logger()

        self.env = env
        self.agent = agent
        self.gamma = gamma

    def experience_generator(self):
        while True:
            state = self.env.reset()

            while True:
                action = self.agent.policy(state)
                n_state, reward, done, info = self.env.step(action)

                yield state, n_state, action, reward, done, info

                if done:
                    break

                state = n_state

    @staticmethod
    def create_generator():
        env = Trade()
        agent = BaseAgent()
        trainer = Trainer(env, agent)
        generator = trainer.experience_generator()

        return generator

    @staticmethod
    def create_one_episode():
        generator = Trainer.create_generator()

        for state, n_state, action, reward, done, info in  generator:
            print(action)



if __name__ == '__main__':

    Trainer.create_one_episode()



