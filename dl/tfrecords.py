
import tensorflow as tf
import numpy as np
import sys
from log import constant
from matplotlib import pylab as plt

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
            'ba_nop': tf.FixedLenFeature([], tf.int64),
            'ba_sell': tf.FixedLenFeature([], tf.int64),
            'ba_buy': tf.FixedLenFeature([], tf.int64),
            'ba_sell_now': tf.FixedLenFeature([], tf.int64),
            'ba_buy_now': tf.FixedLenFeature([], tf.int64),
            'time': tf.FixedLenFeature([], tf.int64)
        })

    board = features['board']

    ba_nop = features['ba_nop']
    ba_sell = features['ba_sell']
    ba_buy = features['ba_buy']
    ba_sell_now = features['ba_sell_now']
    ba_buy_now = features['ba_buy_now']

    ba = [ba_nop, ba_sell, ba_sell_now, ba_buy, ba_buy_now]

    time = features['time']

    print('ba->', ba, ' ', end="")

    return board, ba, time


def decode_buffer(buffer):
    return np.frombuffer(buffer, dtype=np.uint8).reshape(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)


def read_one_tf_file(tffile):
    dataset = tf.data.Dataset.list_files(tffile)
    dataset = tf.data.TFRecordDataset(dataset, compression_type='GZIP')
    dataset = dataset.map(read_tfrecord)
    dataset = dataset.repeat(1)
    dataset = dataset.batch(20000)

    iterator = dataset.make_one_shot_iterator()
    next_dataset = iterator.get_next()

    print("start session")

    boards = None

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        try:
            board_array, ba, time = sess.run(next_dataset)

            boards = np.stack(list(map(decode_buffer, board_array)))
        except tf.errors.OutOfRangeError as e:
            print('End Data')

    return boards, ba, time




