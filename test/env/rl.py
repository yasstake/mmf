import unittest
from env.rl import TradeEnv


class MyTestCase(unittest.TestCase):
    def test_create(self):
        env = TradeEnv()
        self.assertTrue(env is not None)


if __name__ == '__main__':
    unittest.main()
