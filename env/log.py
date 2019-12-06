import os

import tensorflow as tf
from tensorflow import keras

# tf.enable_v2_behavior()

class Logger:
    total_timesteps = tf.train.create_global_step()

    def __init__(self, log_dir='/bitlog/board/'):

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        self._callback = keras.callbacks.TensorBoard(log_dir)

        #self.summary = tf.summary.FileWriter(log_dir)

        # v2 mode
        self.summary = tf.contrib.summary.create_file_writer(log_dir, flush_millis=10000)
        tf.contrib.summary.record_summaries_every_n_global_steps(10)

    def log_loss(self, loss, episode):
        with self.summary.as_default(), tf.contrib.summary.always_record_summaries():
            Logger.total_timesteps.assign(episode)
            tf.contrib.summary.scalar('loss', loss)

    def log_reward(self, episode, reward, total_reward):
        with self.summary.as_default(), tf.contrib.summary.always_record_summaries():
            self.total_timesteps.assign(episode)
            tf.contrib.summary.scalar('loss', reward, step=episode)
            tf.contrib.summary.scalar('reward', reward, step=episode)
            tf.contrib.summary.scalar('total_reward', total_reward, step=episode)

    def log_episode(self, episode, loss, reward, total_reward):
        with self.summary.as_default(), tf.contrib.summary.always_record_summaries():
            self.total_timesteps.assign(episode)
            tf.contrib.summary.scalar('loss', reward, step=episode)
            tf.contrib.summary.scalar('reward', reward, step=episode)
            tf.contrib.summary.scalar('total_reward', total_reward, step=episode)


if __name__ == '__main__':
    log = Logger()

    for i in range(100):
        log.log_loss(i, i)






