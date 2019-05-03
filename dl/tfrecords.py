
import numpy as np
import tensorflow as tf

from log import constant


#def decode_buffer(buffer):
#    return np.frombuffer(buffer, dtype=np.uint8).reshape(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)

def decode_buffer(buffer):
    return np.frombuffer(buffer, dtype=np.uint8).reshape(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH)


def _parse_example(serialized):
    features = tf.io.parse_single_example(
        serialized,
        features={
            'board': tf.io.FixedLenFeature([], tf.string),
            'sell_book_price': tf.io.FixedLenFeature([], tf.float32),
            'sell_book_vol': tf.io.FixedLenFeature([], tf.float32),
            'buy_book_price': tf.io.FixedLenFeature([], tf.float32),
            'buy_book_vol': tf.io.FixedLenFeature([], tf.float32),
            'center_price': tf.io.FixedLenFeature([], tf.float32),
            'sell_trade_price': tf.io.FixedLenFeature([], tf.float32),
            'sell_trade_vol': tf.io.FixedLenFeature([], tf.float32),
            'buy_trade_price': tf.io.FixedLenFeature([], tf.float32),
            'buy_trade_vol': tf.io.FixedLenFeature([], tf.float32),
            'market_buy_price': tf.io.FixedLenFeature([], tf.float32),
            'market_sell_price': tf.io.FixedLenFeature([], tf.float32),
            'fix_buy_price': tf.io.FixedLenFeature([], tf.float32),
            'fix_sell_price': tf.io.FixedLenFeature([], tf.float32),
            'ba': tf.io.FixedLenFeature([], tf.int64),
            'ba_nop': tf.io.FixedLenFeature([], tf.int64),
            'ba_sell': tf.io.FixedLenFeature([], tf.int64),
            'ba_buy': tf.io.FixedLenFeature([], tf.int64),
            'ba_sell_now': tf.io.FixedLenFeature([], tf.int64),
            'ba_buy_now': tf.io.FixedLenFeature([], tf.int64),
            'time': tf.io.FixedLenFeature([], tf.int64),
        })
    return features

def read_tfrecord_board_ba(serialized):
    features = read_tfrecord_example(serialized)

    board = features['board']

    ba_nop = features['ba_nop']
    ba_sell = features['ba_sell']
    ba_buy = features['ba_buy']
    ba_sell_now = features['ba_sell_now']
    ba_buy_now = features['ba_buy_now']

    ba = [ba_nop, ba_sell, ba_sell_now, ba_buy, ba_buy_now]

    time = features['time']

    return board, ba, time


def read_tfrecord_example(serialized):
    features = _parse_example(serialized)

    return features


def read_one_tf_file(tffile):
    dataset = tf.data.Dataset.list_files(tffile)
    dataset = tf.data.TFRecordDataset(dataset, compression_type='GZIP')
    dataset = dataset.map(read_tfrecord_board_ba)
    dataset = dataset.repeat(1)
    dataset = dataset.batch(3000)

    print("start session")

    boards = None

    for data in dataset:
        boards, ba, time = data
        boards = tf.io.decode_raw(boards, tf.uint8)
        boards = tf.reshape(boards, [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

        return boards, ba, time
    
    return None



def calc_class_weight(tffile):
    return {0: 2.4694093218139344, 1: 18.310268982266415, 2: 8.403705676990592, 3: 5.04184874727142, 4: 4.482382766782457}


def _calc_class_weight(tffile):
    with tf.device('/CPU:0'):
        dataset = tf.data.Dataset.list_files(tffile)
        dataset = tf.data.TFRecordDataset(dataset, compression_type='GZIP')
        dataset = dataset.map(read_tfrecord_board_ba)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=20000)
        dataset = dataset.batch(50000)

        print("start session")

        boards = None
        score = np.zeros(5)
        count = 0

        for data in dataset:
            board_array, ba, time = data

            for i in range(0, len(ba)):
                score[np.argmax(ba[i])] += 1
                count += 1

        print(score, count)

        weight = {0:0.0, 1:0.0, 2:0.0, 3:0.0, 4:0.0}

        for i in range(0,5):
            if score[i]:
                weight[i] = count / score[i]
            else:
                weight[i] = 0

        return weight
