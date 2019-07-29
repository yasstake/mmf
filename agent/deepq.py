import numpy as np

import tensorflow as tf
import tensorflow.keras as keras

from agent.base import BaseAgent
from agent.trainer import *
from env.trade import Observation
from env.trade import Trade
from log.constant import *


class Dqn(BaseAgent):

    def __init__(self,epsilon=0.005):
        super().__init__(epsilon)

        #        self.model = self._create_model()
        #        self.teacher_model = self._create_model()
        self.number_of_actions = 5

        self.model = self._create_duel_model()
        self.teacher_model = self._create_duel_model()

    def _create_duel_model(self):

        l_input = keras.layers.Input(shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH))
        conv2d = keras.layers.Conv2D(32, (4, 4), activation='relu', padding='same')(l_input)
        conv2d = keras.layers.Conv2D(64, (2, 2), activation='relu', padding='same')(conv2d)
        conv2d = keras.layers.Conv2D(64, (1, 1), activation='relu', padding='same')(conv2d)
        flat_view = keras.layers.Flatten()(conv2d)

        # sell_reards, buy_rewards
        margin_input = keras.layers.Input(shape=(2,))

        marge_out = keras.layers.concatenate([flat_view, margin_input])

        fltn = keras.layers.Dense(512, activation='relu')(marge_out)

        v = keras.layers.Dense(units=256, activation='relu')(fltn)
        v = keras.layers.Dense(1)(v)
        adv = keras.layers.Dense(256, activation='relu')(fltn)
        adv = keras.layers.Dense(self.number_of_actions)(adv)
        y = keras.layers.concatenate([v, adv])
#        l_output = keras.layers.Dense(self.number_of_actions)(y)
        l_output = keras.layers.Lambda(
            lambda a: keras.backend.expand_dims(a[:, 0], -1) + a[:, 1:] - tf.stop_gradient(keras.backend.mean(a[:, 1:], keepdims=True)),
            output_shape=(self.number_of_actions,))(y)
        model = keras.Model([l_input, margin_input], l_output)

        model.summary()

        model.compile(loss='mse', optimizer='adam')

        return model

    def _create_model(self):

        normal = keras.initializers.glorot_normal()
        optimizer = keras.optimizers.Adam(clipvalue=1.0)

        model = keras.models.Sequential()

        model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH), padding='same', kernel_initializer=normal))
        #model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer=normal))
        #model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer=normal))
        #model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Flatten())
        #model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(units=128))
        model.add(keras.layers.BatchNormalization())
        #model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(units=5, kernel_initializer=normal))
        model.summary()

        model.compile(loss='mse', optimizer=optimizer)

        return model

    def estimate(self, s:Observation):
        #e = self.model.predict([np.expand_dims(s.board, axis=0), np.expand_dims(s.reward, axis=0)])[0]
        e = self.model.predict([np.expand_dims(s.board, axis=0), np.expand_dims(s.rewards, axis=0)])[0]

        if s.is_able_to_buy():
            e[ACTION.BUY_NOW] = self.clip_reward((s.get_buy_now_reward()))
        else:
            e[ACTION.BUY_NOW] = 0
            e[ACTION.BUY] = 0


        if s.is_able_to_sell():
            e[ACTION.SELL_NOW] = self.clip_reward(s.get_sell_now_reward())
        else:
            e[ACTION.SELL_NOW] = 0
            e[ACTION.SELL] = 0

        return e


    def update(self, experiences, gamma):

        batch = sample(experiences, 64)

        states = np.array([e.s.board for e in batch])
        rewards = np.array([e.s.rewards for e in batch])
        #        margin = np.array([e.s.margin for e in batch])
        n_states = np.array([e.n_s.board for e in batch])
        n_rewards = np.array([e.n_s.rewards for e in batch])
        #        n_margin = np.array([e.n_s.margin for e in batch])

        estimated = self.teacher_model.predict([states, n_rewards])
        future = self.teacher_model.predict([n_states, n_rewards])

        for i, e in enumerate(batch):
            if e.s.is_able_to_buy():
                estimated[i][ACTION.BUY] = self.clip_reward(e.s.buy_reward)
                estimated[i][ACTION.BUY_NOW] = self.clip_reward(e.s.get_buy_now_reward())
            else:
                estimated[i][ACTION.BUY_NOW] = 0
                estimated[i][ACTION.BUY] = 0

            if e.s.is_able_to_sell():
                estimated[i][ACTION.SELL] = self.clip_reward(e.s.sell_reward)
                estimated[i][ACTION.SELL_NOW] = self.clip_reward(e.s.get_sell_now_reward())
            else:
                estimated[i][ACTION.SELL_NOW] = 0
                estimated[i][ACTION.SELL] = 0

            reward = e.r

            if not e.d:
                reward += gamma * np.max(future[i])

            estimated[i][e.a] = self.clip_reward(reward)

        loss = self.model.train_on_batch([states, rewards], estimated)

        return loss

    def update_model(self):
        self.teacher_model.set_weights(self.model.get_weights())


if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = Dqn()

#    trainer.train(env, agent, eposode=100000, min_buffer_size=128)
    trainer.train(env, agent, eposode=500000, min_buffer_size=1500)
