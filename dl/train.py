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
                'buy': tf.FixedLenFeature([], tf.string),
                'sell': tf.FixedLenFeature([], tf.string),
                'buy_trade': tf.FixedLenFeature([], tf.string),
                'sell_trade': tf.FixedLenFeature([], tf.string),
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


        buy_order = features['buy']
        sell_order= features['sell']
        buy_trade = features['buy_trade']
        sell_trade = features['sell_trade']
        board_array = [buy_order, sell_order, buy_trade, sell_trade]

        ba_nop = features['ba_nop']
        ba_sell = features['ba_sell']
        ba_buy = features['ba_buy']
        ba_sell_now = features['ba_sell_now']
        ba_buy_now = features['ba_buy_now']
        ba = [ba_nop, ba_sell, ba_buy, ba_sell_now, ba_buy_now]

        time = features['time']

        return  board_array, ba, time


    def board_array_to_np_array(self, board_array):
        board = np.stack([self.decode_buffer(board_array[0]), self.decode_buffer(board_array[1]), self.decode_buffer(board_array[2]), self.decode_buffer(board_array[3])])
        return board


    def decode_buffer(self, buffer):
        return np.frombuffer(buffer, dtype=np.uint8).reshape(constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)


    def create_model(self):
        self.model = Sequential()

        input = keras.Input(shape=(constant.BOARD_WIDTH, constant.BOARD_TIME_WIDTH, constant.NUMBER_OF_LAYERS))
        self.model.add(Dense(units=128, activation='relu')(input))
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
        dataset2 = dataset.map(Train.read_tfrecord)
        iterator = dataset2.make_initializable_iterator()
        next_dataset = iterator.get_next()

        with tf.Session() as sess:
            sess.run(iterator.initializer)

            while True:
                board_array, ba, time = sess.run(next_dataset)

                board = self.board_array_to_np_array(board_array)

                print(board_array.shape, board.shape, time, ba)

        data = np.random.random((1000, 100))
        labels = np.random.randint(10, size=(1000, 1))

        one_hot_labels = keras.utils.to_categorical(labels, num_classes=10)

        model.fit(data, one_hot_labels, epochs=10, batch_size=32)

        print (model.predict(data))

