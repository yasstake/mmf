import os

import tensorflow as tf
from tensorflow import keras

tf.enable_v2_behavior()

class Logger:
    def __init__(self, log_dir='/bitlog/board/'):

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        self._callback = keras.callbacks.TensorBoard(log_dir)

        #self.summary = tf.summary.FileWriter(log_dir)

        # v2 mode
        self.summary = tf.contrib.summary.create_file_writer(log_dir, flush_millis=10000)
        self.total_timesteps = tf.train.create_global_step()
        #  tf.contrib.summary.record_summaries_every_n_global_steps

    def log_loss(self, loss, episode):
        with self.summary.as_default(), tf.contrib.summary.always_record_summaries():
            self.total_timesteps.assign_add(episode)
            tf.contrib.summary.scalar('loss', loss)


    def log_episode(self, episode, loss, reward, total_reward):
        with self.summary.as_default(), tf.contrib.summary.always_record_summaries():
            tf.summary.scalar('loss', reward, step=episode)
            tf.summary.scalar('reward', reward, step=episode)
            tf.summary.scalar('total reward', total_reward, step=episode)


if __name__ == '__main__':
    log = Logger()

    log.log_loss(1, 1)
    log.log_loss(2, 2)
    log.log_loss(3, 3)
    log.log_loss(4, 4)




