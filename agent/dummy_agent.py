from random import sample
from collections import deque
from collections import namedtuple
from log.constant import ACTION
from env.rl import TradeEnv

BUFFER_SIZE = 20000
NUM_OF_EPISODE = 10000

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
        self.episode_no = 0
        self.env = TradeEnv()

    def train(self, episode=NUM_OF_EPISODE):
        for i in range(episode):
            last_q_time = 0

            self.episode_begin(i, None)
            self.env.reset()
            n_state, reward, done, info = self.env.step(ACTION.NOP)
            s = n_state

            while True:
                if not self.env.q_value:
                    break

                if last_q_time != self.env.q_value.time:
                    print(self.env.q_value)
                    last_q_time = self.env.q_value.time

                a = self.env.q_value.get_best_action()

                n_state, reward, done, info = self.env.step(a)
                self.reward += reward

                e = Experience(s, a, reward, n_state, done)
                self.experiences.append(e)

                s = n_state

                if done:
                    break

            self.episode_end(i, s)

    def episode_begin(self, i: int, s):
        pass

    def episode_end(self, i:int, s):
        self.duration = float(self.end_time) - float(self.start_time)
        self.total_reward += self.reward

        s = '<- EPISODE END ({:5d}) '.format(i)
        self.episode_no += 1


if __name__ == '__main__':
    trainer = Trainer()
    trainer.train()
