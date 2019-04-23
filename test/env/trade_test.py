import glob
import unittest

import tensorflow as tf

from env.trade import Trade

tf.enable_v2_behavior()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_list_files(self):
        trade = Trade()

        list = trade.list_tfdata_list()
        print(list)

        print('number of files->', trade.number_of_files)


    def test_glob_files(self):
        files = glob.glob('/bitlog/**/*.tfrecords', recursive=True)

        print(files)
        print(sorted(files))


    def test_new_episode_files(self):
        trade = Trade()

        files = trade._new_episode_files()
        print(files)

    def test_skip_count(self):
        trade = Trade()

        print(trade._skip_count())

    def test_new_episode(self):
        trade = Trade()

        print(trade.new_episode())

    def test_read_one_episode(self):
        trade = Trade()

        episode = trade.new_episode()

        for data in episode:
            board, ba, time = data

            print(time)


if __name__ == '__main__':
    unittest.main()
