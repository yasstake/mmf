import unittest
import numpy as np
import tensorflow as tf

from log.price import PriceBoard

class TfTestCase(unittest.TestCase):
    def feature_int64(self, a):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[a]))

    def feature_bytes(self, a):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[a]))



    def test_save_single_value(self):
        data = 1

        output_file = '/tmp/onevalue.tfrecords'
        pio = tf.python_io

        writer = pio.TFRecordWriter(str(output_file))

        record = tf.train.Example(features=tf.train.Features(feature={
            'time' : self.feature_int64(data)
            }))

        writer.write(record.SerializeToString())

        writer.close()


    def test_load_single_value(self):
        with tf.Session() as sess:
            dataset = tf.data.TFRecordDataset('/tmp/onevalue.tfrecords')
            dataset2 = dataset.map(TfTestCase.read_single_record)
            iterator = dataset2.make_initializable_iterator()
            next_dataset = iterator.get_next()
            sess.run(iterator.initializer)
            time = sess.run(next_dataset)
            sess.close()

        print('time->', time)

    @staticmethod
    def read_single_record(serialized):
        features = tf.parse_single_example(
            serialized,
            features={
                'time': tf.FixedLenFeature([], tf.int64)
            })
        time = features['time']

        return time

    def test_save_file(self):
        board = PriceBoard()

        output_file = '/tmp/data.tfrecords'
        pio = tf.python_io

        #        writer = pio.TFRecordWriter(
        #                      str(output_file), options=pio.TFRecordOptions(pio.TFRecordCompressionType.GZIP))
        writer = pio.TFRecordWriter(str(output_file))

        board.current_time = 1
        record = tf.train.Example(features=tf.train.Features(feature={
            'buy': self.feature_bytes(board.buy_order.tobytes()),
            'time' : self.feature_int64(board.current_time)
            }))

        writer.write(record.SerializeToString())

        writer.close()


    def test_save_file_2rec(self):
        board = PriceBoard()

        output_file = '/tmp/data2.tfrecords'
        pio = tf.python_io

        #        writer = pio.TFRecordWriter(
        #                      str(output_file), options=pio.TFRecordOptions(pio.TFRecordCompressionType.GZIP))
        writer = pio.TFRecordWriter(str(output_file))

        board.current_time = 1
        record = tf.train.Example(features=tf.train.Features(feature={
            'buy': self.feature_bytes(board.buy_order.tobytes()),
            'time' : self.feature_int64(board.current_time)
            }))
        writer.write(record.SerializeToString())

        board.current_time = 2
        record = tf.train.Example(features=tf.train.Features(feature={
            'buy': self.feature_bytes(board.buy_order.tobytes()),
            'time' : self.feature_int64(board.current_time)
            }))
        writer.write(record.SerializeToString())

        writer.close()


    def test_load_file(self):
        with tf.Session() as sess:
            dataset = tf.data.TFRecordDataset('/tmp/data.tfrecords')
            dataset2 = dataset.map(TfTestCase.read_tfrecord)
            iterator = dataset2.make_initializable_iterator()
            next_dataset = iterator.get_next()
            sess.run(iterator.initializer)
            time, buy = sess.run(next_dataset)

        print('time->', time)
        print('buy->', buy)

        buy2D = np.frombuffer(buy, dtype=np.uint8)

        print(buy2D)

    def test_load_file_2rec(self):
        dataset = tf.data.TFRecordDataset('/tmp/data2.tfrecords')
        dataset2 = dataset.map(TfTestCase.read_tfrecord)
        iterator = dataset2.make_one_shot_iterator()
        next_dataset = iterator.get_next()

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())


            time, buy = sess.run(next_dataset)
            buy2D = np.frombuffer(buy, dtype=np.uint8)
            print('time->', time)
            print(buy2D)

            time, buy = sess.run(next_dataset)
            buy2D = np.frombuffer(buy, dtype=np.uint8)

            print('time->', time)
            print(buy2D)

            # end of data
            #time, buy = sess.run(next_dataset)
            #self.assertEqual(time, None)






    @staticmethod
    def read_tfrecord(serialized):
        buy = None
        time = None

        features = tf.parse_single_example(
            serialized,
            features={
                'buy': tf.FixedLenFeature([], tf.string),
                'time': tf.FixedLenFeature([], tf.int64)
            })

        buy = features['buy']
        time = features['time']

        return time, buy


if __name__ == '__main__':
    unittest.main()
