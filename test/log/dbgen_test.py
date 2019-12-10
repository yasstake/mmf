import unittest
from log.dbgen import Generator

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_create_generator(self):
        g = Generator()
        gen1 = g.create(db_name='/bitlog/bitlog.db')
        gen2 = g.create(db_name='/bitlog/bitlog.db')

        for i in range(100):
            board = next(gen1)
            print('a', board.current_time, board.center_price)

            board = next(gen2)
            print('B', board.current_time, board.center_price)


if __name__ == '__main__':
    unittest.main()
