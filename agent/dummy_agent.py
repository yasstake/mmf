import numpy as np
from autokeras import ImageRegressor
from random import sample
from collections import deque
from collections import namedtuple
from log.constant import ACTION
from env.rl import TradeEnv

BUFFER_SIZE = 200000
NUM_OF_EPISODE = 10

Experience = namedtuple('Experience', ['s', 'a', 'r', 'n_s', 'd'])
QState = namedtuple('QState', ['s', 'q'])


class Trainer:
    def __init__(self, buffer_size=BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.experiences = deque(maxlen=self.buffer_size)
        self.q_values = deque(maxlen=self.buffer_size)
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
                    last_q_time = self.env.q_value.time

                a = self.env.q_value.get_best_action()

                if a != ACTION.NOP:
                    print(self.env.q_value)

                n_state, reward, done, info = self.env.step(a)
                self.reward += reward

                if (n_state is not None) and (self.env.q_value is not None):
                    q = QState(n_state, self.env.q_value)
                    self.q_values.append(q)

                s = n_state

                if done:
                    break

            self.episode_end(i, s)
            np.savez_compressed('/tmp/q_values.npz', self.q_values)

            states = np.array([q.s for q in self.q_values])
            q_values = np.array([q.q.to_array() for q in self.q_values])

            states = states.reshape(states.shape)
            q_values = q_values.reshape(q_values.shape)

            np.savez_compressed('/tmp/q_stats.npz', s=states, q=q_values)

    def learning(self):
        npz = np.load('/tmp/q_stats.npz')

        states = npz['s']
        q_values = npz['q']

        print('stateshape', states.shape)
        print('qvalueshape', q_values.shape)

        reg = ImageRegressor(output_dim=5, seed=12314, max_trials=3)

        reg.fit(states, q_values, validation_split=0.2, epochs=2)

    def create_image_regressor(self):
        pass


    def episode_begin(self, i: int, s):
        pass

    def episode_end(self, i:int, s):
        self.duration = float(self.end_time) - float(self.start_time)
        self.total_reward += self.reward

        s = '<- EPISODE END ({:5d}) TOTAL{:5.2f}'.format(i, self.total_reward)
        self.episode_no += 1


if __name__ == '__main__':
    trainer = Trainer()
    #trainer.train()
    trainer.learning()
