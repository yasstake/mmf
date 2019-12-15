import unittest
from log.dbgen import PriceBoard


class MyTestCase(unittest.TestCase):
    def test_create(self):
        board = PriceBoard()
        self.assertIsNotNone(board)




if __name__ == '__main__':
    unittest.main()
