import unittest


import tensorflow as tf

tf.enable_v2_behavior()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_tf_queue(self):

        queue = tf.RandomShuffleQueue(capacity=10000, shared_name='REPLAY_BUFFER')


        queue.enqueue('a')


    def test_tensor_board(self):
        pass


if __name__ == '__main__':
    unittest.main()
