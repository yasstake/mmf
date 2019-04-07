import unittest

import tensorflow as tf
import tensorflow.python.keras as keras
from dl.train import Train
import numpy as np
class TFFileTest(unittest.TestCase):

    def test_train_data_set(self):
        input_dataset = tf.data.Dataset.list_files('/tmp/**/*.tfrecords')
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset.cache('/tmp/data.cache')
        dataset = dataset.map(Train.read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=1000)
        dataset = dataset.batch(50000)

        return dataset

    def test_do_train(self, train_pattern, test_pattern):
        train_dataset = self.train_data_set(train_pattern)
        test_dataset = self.test_data_set(test_pattern)

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

                    boards = np.stack(list(map(Train.decode_buffer, board_array)))

                    best = keras.utils.to_categorical(ba)
                    #self.model.fit(boards, best, batch_size=128)

                except tf.errors.OutOfRangeError as e:
                    print('training end')
                    break
                    pass


    def test_list_blobs(self):

        data_set = tf.data.Dataset.list_files(('/tmp/2019/**/*.tfrecords'))

        iter = tf.data.make_one_shot_iterator(data_set)

        for item in iter:
            print(item)

        print(data_set)

        pass

    @staticmethod
    def stack(*inputs):
        return tf.stack(inputs)

    def test_tf_records(self):

        D1 = tf.data.Dataset('a', 'b', 'c')
        D2 = tf.data.Dataset.range(5,10)
        D3 = tf.data.Dataset.range(10,15)

        D = tf.data.Dataset.zip((D1,D2,D3))
        D = D.map(TFFileTest.stack)
        D = D.apply(tf.contrib.data.unbatch())
        D = D.shuffle(10, seed=0)
        D = D.batch(3)
        D = D.prefetch(1)

        it = D.make_one_shot_iterator()
        next_element = it.get_next()

        with tf.Session() as sess:
            print(sess.run(next_element))
