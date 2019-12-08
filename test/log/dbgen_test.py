import unittest
from log.dbgen import Generator

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_create_generator(self):
        gen1 = Generator.create(db_name='/bitlog/bitlog.db')
        gen2 = Generator.create(db_name='/bitlog/bitlog.db')

        for i in range(10):
            board = next(gen1)
            print(board.current_time, board.center_price)

            board = next(gen2)
            print(board.current_time, board.center_price)


if __name__ == '__main__':
    unittest.main()
