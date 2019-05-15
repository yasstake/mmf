from collections import deque
from collections import namedtuple

from agent.deepq import *
from env.log import Logger

BUFFER_SIZE = 20000

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd', 'q'])


class HP:
    NETWORK_UPDATE_CYCLE = 2




class Trainer():
    def __init__(self, env, agent, gamma=0.99, buffer_size=BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.local_buffer = deque(maxlen=self.buffer_size)
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

    def create_generator(self):
        trainer = Trainer(self.env, self.agent)
        generator = trainer.experience_generator()

        return generator

    def create_one_episode(self):


        print('episode end', len(self.local_buffer))

        episode_len = len(self.local_buffer)
        for i, e in enumerate(reversed((self.local_buffer))):
            pass

    def compute_priority(self):
        pass

    def add_replay_buffer(self):
        pass

    def one_episode(self):
        # Obtain latest network parameters
        # Initialize Environment
        generator = self.create_generator()

        for state, n_state, action, reward, done, info in generator:
            self.local_buffer.append(Experience(state, action, reward, n_state, done, None))
            if done:
                break

        self.compute_priority()

        # replay add
        self.add_replay_buffer()


if __name__ == '__main__':
    env = Trade()
    agent = BaseAgent()

    trainer = Trainer(env, agent)

    trainer.create_one_episode()




