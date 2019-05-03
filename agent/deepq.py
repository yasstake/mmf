import tensorflow.contrib.keras as keras

from agent.base import *
from log.constant import *


class Dqn(BaseAgent):

    def __init__(self,epsilon=0.1):
        super().__init__(epsilon)

        self.model = None
        self.teacher_model = None


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
        model.add(keras.layers.Dense(units=5, activation='softmax'))
        model.summary()

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return model


    def create_model(self, feature_shape):
        self.model = self._create_model()
        self.teacher_model = self._create_model()



    def estimate(self, s):
        return self.model.predict(np.array(s))[0]

    def update(self, experiences, gamma):
        states = np.array([e.s for e in experiences])
        n_states = np.array([e.n_s for e in experiences])

        estimateds = self.model.predict(states)
        future = self.teacher_model.predict(n_states)



        pass




