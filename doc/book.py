#!pip install -q matplotlib-venn


import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import tensorflow.python.keras as keras
import numpy as np

TIME_WIDTH = 128
BOARD_WIDTH = 32
BOARD_TIME_WIDTH = TIME_WIDTH
NUMBER_OF_LAYERS = 4

class ACTION:
    NOP =           0
    BUY =      0b0001
    SELL =     0b0010
    BUY_NOW =  0b0100
    SELL_NOW = 0b1000


model = None

def read_tfrecord(serialized):
    buy = None
    time = None

    features = tf.parse_single_example(
    serialized,
    features={
    'board': tf.FixedLenFeature([], tf.string),
    'market_buy_price': tf.FixedLenFeature([], tf.float32),
    'market_sell_price': tf.FixedLenFeature([], tf.float32),
    'fix_buy_price': tf.FixedLenFeature([], tf.float32),
    'fix_sell_price': tf.FixedLenFeature([], tf.float32),
    'ba': tf.FixedLenFeature([], tf.int64),
    'ba_nop': tf.FixedLenFeature([], tf.float32),
    'ba_sell': tf.FixedLenFeature([], tf.float32),
    'ba_buy': tf.FixedLenFeature([], tf.float32),
    'ba_sell_now': tf.FixedLenFeature([], tf.float32),
    'ba_buy_now': tf.FixedLenFeature([], tf.float32),
    'time': tf.FixedLenFeature([], tf.int64)
    })

    board = features['board']

    ba_nop = features['ba_nop']
    ba_sell = features['ba_sell']
    ba_buy = features['ba_buy']
    ba_sell_now = features['ba_sell_now']
    ba_buy_now = features['ba_buy_now']
    ba = [ba_nop, ba_sell, ba_buy, ba_sell_now, ba_buy_now]

    time = features['time']

    return  board, ba, time


def decode_buffer(buffer):
    return np.frombuffer(buffer, dtype=np.uint8).reshape(NUMBER_OF_LAYERS, BOARD_TIME_WIDTH, BOARD_WIDTH)

def create_model():
    model = Sequential()

    model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH), padding='same'))
    model.add(keras.layers.MaxPooling2D((2,2)))

    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dropout(0.4))
    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=5, activation='softmax'))

    model.summary()

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

    return model


def train_data_set(self, file_pattern):
    print('train', file_pattern)

    input_dataset = tf.data.Dataset.list_files(file_pattern)
    dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
    dataset.cache('/tmp/data.cache')
    dataset = dataset.map(read_tfrecord)
    dataset = dataset.repeat(1)
    dataset = dataset.shuffle(buffer_size=100000)
    dataset = dataset.batch(50000)

    return dataset

def test_data_set(self, file_pattern):
    print(file_pattern)

    input_dataset = tf.data.Dataset.list_files(file_pattern)
    dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
    dataset = dataset.map(read_tfrecord)
    dataset = dataset.repeat(1)
    dataset = dataset.shuffle(buffer_size=10000)
    dataset = dataset.batch(5000)

    return dataset


def do_train(self, train_pattern, test_pattern):
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

                self.model.fit(boards, ba, batch_size=128)

            except tf.errors.OutOfRangeError as e:
                print('training end')
                break


            # Evaluate
        try:
            board_array, ba, time = sess.run(test_next_dataset)
            boards = np.stack(list(map(decode_buffer, board_array)))

            result = self.model.evaluate(boards, ba)
            print('evaluation->', result)

            print(self.model.predict(boards[0]))

        except tf.errors.OutOfRangeError as e:
            pass


