import glob
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.utils import to_categorical

import tensorflow.python.keras as keras
import numpy as np
import random

from log  import constant
from log.constant import ACTION
from log.price import PriceBoard
from dl.tfrecords import read_tfrecord
from dl.tfrecords import decode_buffer
from dl.tfrecords import calc_class_weight


class Train:
    def __init__(self):
        self.model = None
        pass

    @staticmethod
    def loss_function(y_true, y_pred):
        pass
        #return keras.K.mean(K.abs(y_pred - y_true))

    def create_model(self):
        self.model = Sequential()

        self.model.add(keras.layers.Conv2D(128, (2, 2), activation='relu', input_shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH), padding='same'))
        self.model.add(keras.layers.Flatten())
        self.model.add(keras.layers.Dropout(0.4))
        self.model.add(keras.layers.BatchNormalization())
        self.model.add(Dense(units=5, activation='softmax'))

        self.model.summary()

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


    def train_data_set(self, file_pattern):
        print('train', file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset.cache('/tmp/data.cache')
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(5000)

        return dataset

    def test_data_set(self, file_pattern):
        print(file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(5)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(5000)

        return dataset


    def do_train(self, train_pattern, test_pattern):
        weight = calc_class_weight(train_pattern)

        print('weight->', weight)

        train_dataset = self.train_data_set(train_pattern)
        test_dataset  = self.test_data_set(test_pattern)

        train_iterator = train_dataset.make_initializable_iterator()
        train_next_dataset = train_iterator.get_next()

        test_iterator = test_dataset.make_one_shot_iterator()
        test_next_dataset = test_iterator.get_next()

        print("start session")

                
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(train_iterator.initializer)

            while True:
                try:
                    board_array, ba, time = sess.run(train_next_dataset)

                    boards = np.stack(list(map(decode_buffer, board_array)))

                    self.model.fit(boards, ba, batch_size=128, class_weight=weight)

                except tf.errors.OutOfRangeError as e:
                    print('training end')
                    break
                    pass

            # Evaluate
            try:
                board_array, ba, time = sess.run(test_next_dataset)
                boards = np.stack(list(map(decode_buffer, board_array)))

                loss, acc = self.model.evaluate(boards, ba)
                print('evaluation->', loss, acc)

            except tf.errors.OutOfRangeError as e:
                pass

            path = '/tmp/bitmodel.h5'
            self.model.save(path)

    def load_model(self, path):
        self.model = keras.models.load_model(path)

    def predict(self, board):

        result = self.model.predict_proba((board))

        return result
