import time
import threading
import sys

from tensorflow import keras

from agent.deepq import *
from env.log import Logger
from random import sample

BUFFER_SIZE = 20000


class Experience:
    def __init__(self, state, action, reward, next_state, done, q_values=None):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done
        self.q_values = q_values

class HP:
    NETWORK_UPDATE_CYCLE = 2
    TIME_PENALTY = -0.00001

    def __init__(self):
        pass


class Agent(BaseAgent):
    global_brain = None

    def __init__(self):
        super(Agent, self).__init__()
        self.total_reward = 0

        if Agent.global_brain is None:
            Agent.global_brain = self.create_brain()
        self.local_brain = self.create_brain()
        self.copy_brain_to_local()

    def create_brain_3(self):
        l_input = keras.layers.Input(shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH))

        conv2d = keras.layers.Conv2D(32, (4, 4), activation='relu', padding='same')(l_input)
        conv2d = keras.layers.Conv2D(64, (1, 1), activation='relu', padding='same')(conv2d)
        flat_view = keras.layers.Flatten()(conv2d)
        flat_view = keras.layers.Dense(512, activation='relu')(flat_view)

        margin_input = keras.layers.Input(shape=(4,))
        margin_input2 = keras.layers.Dense(32, activation='relu')(margin_input)

        marge_out = keras.layers.concatenate([flat_view, margin_input2])

        fltn = keras.layers.Dense(512, activation='relu')(marge_out)
        fltn = keras.layers.Dense(128, activation='relu')(fltn)
        l_output = keras.layers.Dense(self.number_of_actions)(fltn)

        model = keras.Model([l_input, margin_input], l_output)

        model.summary()

        model.compile(loss='mse', optimizer='adam')

        return model

    def create_brain(self):
        l_input = keras.layers.Input(shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH))

        conv2d = keras.layers.Conv2D(32, (4, 4), activation='relu', padding='same')(l_input)
        conv2d = keras.layers.Conv2D(64, (1, 1), activation='relu', padding='same')(conv2d)
        flat_view = keras.layers.Flatten()(conv2d)
        flat_view = keras.layers.Dense(1024, activation='relu')(flat_view)
        flat_view = keras.layers.Dense(512, activation='relu')(flat_view)

        margin_input = keras.layers.Input(shape=(4,))
        margin_input2 = keras.layers.Dense(64, activation='relu')(margin_input)
        margin_input2 = keras.layers.Dense(32, activation='relu')(margin_input2)

        marge_out = keras.layers.concatenate([flat_view, margin_input2])

        fltn = keras.layers.Dense(512, activation='relu')(marge_out)
        fltn = keras.layers.Dense(256, activation='relu')(fltn)
        fltn = keras.layers.Dense(128, activation='relu')(fltn)
        l_output = keras.layers.Dense(self.number_of_actions)(fltn)

        model = keras.Model([l_input, margin_input], l_output)

        model.summary()

        model.compile(loss='mse', optimizer='adam')

        return model




    def create_brain2(self):
        l_input = keras.layers.Input(shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH))
        conv2d = keras.layers.Conv2D(32, (4, 4), activation='relu', padding='same')(l_input)
        conv2d = keras.layers.Conv2D(64, (2, 2), activation='relu', padding='same')(conv2d)
        conv2d = keras.layers.Conv2D(64, (1, 1), activation='relu', padding='same')(conv2d)
        flat_view = keras.layers.Flatten()(conv2d)

        margin_input = keras.layers.Input(shape=(4,))

        marge_out = keras.layers.concatenate([flat_view, margin_input])

        fltn = keras.layers.Dense(512, activation='relu')(marge_out)

        v = keras.layers.Dense(units=256, activation='relu')(fltn)
        v = keras.layers.Dense(1)(v)
        adv = keras.layers.Dense(256, activation='relu')(fltn)
        adv = keras.layers.Dense(self.number_of_actions)(adv)
        y = keras.layers.concatenate([v, adv])
        #        l_output = keras.layers.Dense(self.number_of_actions)(y)
        l_output = keras.layers.Lambda(
        lambda a: keras.backend.expand_dims(a[:, 0], -1) + a[:, 1:] - tf.stop_gradient(
            keras.backend.mean(a[:, 1:], keepdims=True)),
        output_shape=(self.number_of_actions,))(y)
        model = keras.Model([l_input, margin_input], l_output)

        model.summary()

        model.compile(loss='mse', optimizer='adam')

        return model

    def copy_brain_to_local(self):
        self.local_brain.set_weights(Agent.global_brain.get_weights())

    def estimate(self, status):
        e = self.predict(status)

        return e
        '''
        if status.is_able_to_buy():
            if status.buy_reward:
                e[ACTION.BUY] = status.buy_reward
            if status.get_buy_now_reward():
                e[ACTION.BUY_NOW] = status.get_buy_now_reward()
        else:
            e[ACTION.BUY_NOW] = HP.TIME_PENALTY
            e[ACTION.BUY] = HP.TIME_PENALTY

        if status.is_able_to_sell():
            if status.sell_reward:
                e[ACTION.SELL] = status.sell_reward
            if status.get_sell_now_reward():
                e[ACTION.SELL_NOW] = status.get_sell_now_reward()
        else:
            e[ACTION.SELL_NOW] = HP.TIME_PENALTY
            e[ACTION.SELL] = HP.TIME_PENALTY

        return e
        '''

    def train(self, s, r, q):
        return self.global_brain.train_on_batch([s, r], q)

    def predict(self, s, use_global_brain = False):
        brain = None

        if use_global_brain:
            brain = self.global_brain
        else:
            brain = self.local_brain

        e = brain.predict([np.expand_dims(s.board, axis=0), np.expand_dims(s.rewards, axis=0)])[0]

        return e



class Trainer():

    experiences_len = 500000
    experiences = deque(maxlen=experiences_len)

    def __init__(self, env, agent, gamma=0.99, buffer_size=BUFFER_SIZE, name=''):
        self.buffer_size = buffer_size
        self.local_buffer = deque(maxlen=self.buffer_size)
        self.reward = 0
        self.start_time = 0
        self.end_time = 0
        self.loss = None
        self.total_reward = 0
        self.duration = 0

        self.env = env
        self.agent = agent
        self.gamma = gamma

        self.name = name

    def experience_generator(self):
        while True:
            state = self.env.reset()

            while True:
                action = self.agent.policy(state)
                result = self.env.step(action)

                if result:
                    n_state, reward, done, info = result
                    yield state, n_state, action, reward, done, info
                else:
                    yield None

                if done:
                    print('eposode done')
                    break

                state = n_state

    def create_generator(self):
        generator = self.experience_generator()
        return generator

    def calc_multi_step_q_value(self, start_index, steps, gamma=0.99):
        '''
        calc q value in reverse order.
            [t][t-1][t-2][t-3]......
        :param start_index:
        :param steps:
        :return:
        '''
        buffer_size = len(self.local_buffer)
        print('len', buffer_size)

        reward = 0

        while buffer_size:
            buffer_size -= 1
            steps -= 1

            experience = self.local_buffer[start_index + buffer_size]
            if experience.done:
                print('done', reward)

                reward += gamma * experience.reward
                break

            if buffer_size == 1 or steps <= 1:
                reward += gamma * np.argmax(experience.q_values)
                break

            reward += gamma * experience.q_values[experience.action]

        experience = self.local_buffer[start_index]
        action = experience.action

        self.local_buffer[start_index].q_values[action] = reward
        self.local_buffer[start_index].q_values = self.clip_reward(self.local_buffer[start_index].q_values)

    def clip_reward(self, rewards, clip = 50):
        for i, r in enumerate(rewards):
            if clip < r:
                rewards[i] = clip
            elif r < -clip:
                rewards[i] = -clip

        return rewards

    def predict_q_values(self, status):
        e = self.agent.estimate(status)

        return e

    # old version
    def _predict_q_values(self, status):
        e = self.agent.estimate(status)

        if status.is_able_to_buy():
            reward = status.get_buy_now_reward()
        if reward is not None:
            e[ACTION.BUY_NOW] = reward


        else:
            e[ACTION.BUY_NOW] = 0
            e[ACTION.BUY] = 0

        if status.is_able_to_sell():
            reward = status.get_sell_now_reward()
            if reward is not None:
                e[ACTION.SELL_NOW] = reward
        else:
            e[ACTION.SELL_NOW] = 0
            e[ACTION.SELL] = 0

        return e

    def one_step_in_episode_generator(self):
        while True:
            buffer = self.one_episode()

            for s in buffer:
                yield s

    def one_episode(self):
        # Obtain latest network parameters
        # Initialize Environment
        generator = self.create_generator()

        buffer = []

        for s in generator:
            if s:
                state, n_state, action, reward, done, info = s
                estimate = self.predict_q_values(state)
                buffer.append(Experience(state, action, reward, n_state, done, estimate))
                if done:
                    break

        buffer = self.update_q_values(buffer)
        return buffer

    def update_q_values(self, experiences):
        experiences.reverse()

        reward = None
        for e in experiences:
            if e.state.is_able_to_sell():
                r = e.state.get_sell_now_reward()
                if r:
                    e.q_values[ACTION.SELL_NOW] = r

                r = e.state.sell_reward
                if r:
                    e.q_values[ACTION.SELL] = r
            else:
                e.q_values[ACTION.SELL_NOW] = 0
                e.q_values[ACTION.SELL] = 0

            if e.state.is_able_to_buy():
                r = e.state.get_buy_now_reward()
                if r:
                    e.q_values[ACTION.BUY_NOW] = r

                r = e.state.buy_reward
                if r:
                    e.q_values[ACTION.BUY] = r
            else:
                e.q_values[ACTION.BUY_NOW] = 0
                e.q_values[ACTION.BUY] = 0

            if reward is None:
                reward = e.reward
                # todo assign max of next state value

            action = e.next_state.action
            e.q_values[action] = reward

        experiences.reverse()
        return experiences

    def init_buffer(self, size=200):
        print('prepare')
        agent = trainer.one_step_in_episode_generator()

        for step in agent:
            Trainer.experiences.append(step)
            if size < len(Trainer.experiences):
                self.agent.set_initialized()
                break

    def append_new_experience(self):
        agent = trainer.one_step_in_episode_generator()

        while True:
            try:
                for step in agent:
                    Trainer.experiences.append(step)
            except Exception as e:
                tb = sys.exc_info()[2]
                print('error in new experiences{0}'.format(e.with_traceback(tb)))

    def train_global_brain(self, batch_size=32, train_loop=1000):
        while True:
            for _ in range(train_loop):
                batch = sample(Trainer.experiences, batch_size)

                states = np.array([e.state.board for e in batch])
                rewards = np.array([e.state.rewards for e in batch])
                q_values = np.array([e.q_values for e in batch])

                loss = agent.train(states, rewards, q_values)
                print('loss->', loss)

            print("copy_brain to local")
            self.agent.copy_brain_to_local()


if __name__ == '__main__':
    env = Trade(name='#1')
    agent = Agent()

    trainer = Trainer(env, agent)

    trainer.init_buffer(10000)
    print('init end')

    thread = threading.Thread(target=trainer.append_new_experience)
    thread.start()

    '''
    env2 = Trade(name='#2')
    agent2 = Agent()

    trainer2 = Trainer(env2, agent2)

    thread2 = threading.Thread(target=trainer2.append_new_experience)
    thread2.start()
    '''
    print('start training')
    thread3 = threading.Thread(target=trainer.train_global_brain)
    thread3.start()

