import unittest

import tensorflow as tf

from log.price import PriceBoard

class TfTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def feature_int64(self, a):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[a]))

    def feature_bytes(self, a):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[a]))

    def test_save_file(self):
        board = PriceBoard()

        output_file = '/tmp/data.tfrecords'
        pio = tf.python_io

        #        writer = pio.TFRecordWriter(
        #                      str(output_file), options=pio.TFRecordOptions(pio.TFRecordCompressionType.GZIP))
        writer = pio.TFRecordWriter(str(output_file))

        board.current_time = 1
        record = tf.train.Example(features=tf.train.Features(feature={
            'time' : self.feature_int64(board.current_time)
            }))

        writer.write(record.SerializeToString())

        board.current_time = 100
        record = tf.train.Example(features=tf.train.Features(feature={
            'time' : self.feature_int64(board.current_time)
            }))

        writer.write(record.SerializeToString())

        writer.close()


    def test_load_file(self):
        board = PriceBoard()

        input_file = '/tmp/data.tfrecords'


        data_set = tf.data.TFRecordDataset(input_file)

        example = tf.train.Example()

        data = example.ParseFromString(data_set)

        print(data)


    def test_load_file2(self):
        with tf.Session() as sess:
            dataset = tf.data.TFRecordDataset('/tmp/data.tfrecords')
            dataset = dataset.map(TfTestCase.read_tfrecord)
            iterator = dataset.make_initializable_iterator()
            next_dataset = iterator.get_next()
            sess.run(iterator.initializer)

            for i in range(2):
                time =sess.run(next_dataset)
                print('time->', time)
            sess.close()

    @staticmethod
    def read_tfrecord(serialized):
        features = tf.parse_single_example(
        serialized,
        features={
        'time': tf.FixedLenFeature([], tf.int64)
        })
        time = tf.cast(features['time'], tf.int32)

        return time





if __name__ == '__main__':
    unittest.main()
