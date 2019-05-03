import tensorflow.keras as keras

from agent.base import *
from agent.trainer import Trainer
from log.constant import *


class Dqn(BaseAgent):

    def __init__(self,epsilon=0.1):
        super().__init__(epsilon)

        self.model = self._create_model()
        self.teacher_model = self._create_model()


    def _create_model(self):
        model = keras.models.Sequential()

        model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH), padding='same'))
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Flatten())
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Dropout(0.4))
        model.add(keras.layers.Dense(units=5, activation='linear'))
        model.summary()

        model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

        return model

    def estimate(self, s):
        e = self.model.predict(np.expand_dims(s.board, axis=0))[0]

        print('estimated->', e)

        return e

    def update(self, experiences, gamma):
        states = np.array([e.s.board for e in experiences])
        n_states = np.array([e.n_s.board for e in experiences])

        estimated = self.model.predict(states)

        future = self.teacher_model.predict(n_states)

        for i, e in enumerate(experiences):
            reward = e.r

            if not e.d:
                reward += gamma * np.max(future[i])

            estimated[i][e.a] = reward

        loss = self.model.train_on_batch(states, estimated)

        return loss

    def update_model(self):
        self.teacher_model.set_weights(self.model.get_weights())


if __name__ == '__main__':
    trainer = Trainer()
    env = Trade()
    agent = Dqn()

    trainer.train(env, agent, eposode=100)
