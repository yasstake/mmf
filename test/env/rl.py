import unittest
from env.rl import TradeEnv


class MyTestCase(unittest.TestCase):
    def test_create(self):
        env = TradeEnv()
        self.assertTrue(env is not None)

    def test_list_files(self):
        env = TradeEnv()
        files = env._list_tfdata()
        print(files)

    def test_reset(self):
        env = TradeEnv()
        env.reset()

    def test_step(self):
        env = TradeEnv()
        env.step(1)

    def test_render(self):
        env = TradeEnv()
        env.render()

    def test_close(self):
        env = TradeEnv()
        env.close()

    def test_seed(self):
        env = TradeEnv()
        env.seed()

    def test_new_file_index(self):
        env = TradeEnv()
        index = env._new_file_index()
        print('new file index = ', index)

    def test_skip_count(self):
        '''
        return int(random.random() * (BOARD_IN_FILE * 0.95))
        '''
        env = TradeEnv()
        skip_count = env._skip_count()
        print('skip count = ', skip_count)

    def test_new_episode_files(self):
        '''
        start = self._new_file_index()
        end = start + EPISODE_FILES + 1

        files = self.data_files[start:end]

        return files
        '''
        env = TradeEnv()
        files = env._new_episode_files()
        print('- NEW EPISODE FILES-')
        print(files)


    def test_new_episode(self):
        '''
        start = self._new_file_index()
        end = start + EPISODE_FILES + 1
        skip = self._skip_count()

        return self._new_episode(start, end, skip)
        '''
        env = TradeEnv()
        env.new_episode()

    def test_generator(self):
        env = TradeEnv()
        g1 = env.new_sec_generator()
        g2 = env.new_sec_generator()

        next(g1)
        next(g2)

if __name__ == '__main__':
    unittest.main()
