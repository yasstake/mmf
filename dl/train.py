import glob
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import tensorflow.python.keras as keras
import numpy as np

from log  import constant
from log.price import PriceBoard



class Train:
    def __init__(self):
        self.model = None
        pass

    @staticmethod
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

    @staticmethod
    def decode_buffer(buffer):
        return np.frombuffer(buffer, dtype=np.uint8).reshape(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)

    def create_model(self):
        self.model = Sequential()

        input = keras.Input(shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH))

        self.model.add(keras.layers.Conv2D(32, (2, 2), activation='relu', input_shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)))

        self.model.add(keras.layers.MaxPooling2D((3,3)))
        self.model.add(keras.layers.Flatten())
        self.model.add(Dense(units=32, activation='relu'))
        self.model.add(Dense(units=5, activation='softmax'))

        self.model.summary()

        self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

        def load_tf_dataset(self, file_pattern):
            files = sorted(glob.glob(file_pattern, recursive=True))

            # files = tf.gfile.Glob(file_pattern)

            print(files)

            input_dataset = tf.data.Dataset.list_files(files)
            dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
            dataset2 = dataset.map(PriceBoard.read_tfrecord)
            iterator = dataset2.make_initializable_iterator()
            next_dataset = iterator.get_next()

            with tf.Session() as sess:
                sess.run(iterator.initializer)

                while True:
                    buy, sell, buy_trade, sell_trade, market_buy_price, \
                    market_sell_price, fix_buy_price, fix_sell_price, ba, ba_sell, ba_buy, ba_sell_now, ba_buy_now, time = sess.run(
                        next_dataset)

                    print(time, ba_sell)

    def do_train(self, file_pattern):
        files = sorted(glob.glob(file_pattern, recursive=True))

        print(files)

        input_dataset = tf.data.Dataset.list_files(files)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset = dataset.map(Train.read_tfrecord)
        dataset = dataset.repeat(20)
        dataset = dataset.shuffle(buffer_size=100000)
        dataset = dataset.batch(2048)

        iterator = dataset.make_initializable_iterator()
        next_dataset = iterator.get_next()

        with tf.Session() as sess:
            sess.run(iterator.initializer)

            while True:
                try:
                    board_array, ba, time = sess.run(next_dataset)

                    boards = np.stack(list(map(Train.decode_buffer, board_array)))

                    self.model.fit(boards, ba, batch_size=64)

                except tf.errors.OutOfRangeError as e:
                    break



