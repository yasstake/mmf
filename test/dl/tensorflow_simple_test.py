import unittest

import tensorflow as tf


class MyTestCase(unittest.TestCase):
    def test_simple_add(self):
#        a = tf.constant(1, name='a')
#        b = tf.constant(2, name='b')

        a = tf.constant(1)
        b = tf.constant(2)

        c = a + b

        print(c)

#        graph = tf.get_default_graph()
#        print(graph.as_graph_def())

        with tf.Session() as sess:
            print(sess.run(c))

    def test_simple_var_add(self):
        a = tf.Variable(1, name='a')
        b = tf.constant(2, name='b')

        c = tf.assign(a, a + b)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            print(sess.run(a))
            print(sess.run(c))
            print(sess.run(c))



if __name__ == '__main__':
    unittest.main()
