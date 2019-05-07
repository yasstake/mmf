import os

import tensorflow as tf
from tensorflow import keras


class Logger:
    def __init__(self, log_dir='/bitlog/board/'):

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        self._callback = keras.callbacks.TensorBoard(log_dir)

        #self.summary = tf.summary.FileWriter(log_dir)
        self.summary = tf.contrib.summary.create_file_writer(log_dir)

    def write(self, index, name, value):
        if value:
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.tag = name
            summary_value.simple_value = value
#            self.summary.add_summary(summary, index)
            self.summary.flush()


if __name__ == '__main__':
    log = Logger()

    log.write(1, 'loss', 0.1)
    log.write(1, 'reward', 0.1)

    log.write(2, 'loss', 0.2)
    log.write(2, 'reward', 0.3)

    log.write(3, 'loss', 0.4)
    log.write(3, 'reward', 0.5)

    log.write(4, 'loss', 0.5)
    log.write(4, 'reward', 0.7)

