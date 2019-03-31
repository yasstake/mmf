import unittest

import tensorflow as tf
import tensorflow.data as tfds

class TFFileTest(unittest.TestCase):

    tf.data.TFRecordDataset



    def test_list_blobs(self):


        data_set = tf.data.Dataset.list_files(('/tmp/2019/**/*.tfrecords'))

        iter = tf.data.make_one_shot_iterator(data_set)

        for item in iter:
            print(item)

        print(data_set)

        pass

