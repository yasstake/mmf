import unittest
from log.dbgen import Generator

class MyTestCase(unittest.TestCase):
    def test_create_generator(self):
        g = Generator()
        gen1 = g.create(db_name='/bitlog/bitlog.db')
        gen2 = g.create(db_name='/bitlog/bitlog.db')

        for i in range(1000):
            board = next(gen1)
            print('a', board.current_time, board.center_price)
            a = board.get_std_boards()
    #        print(board.get_std_boards())


if __name__ == '__main__':
    unittest.main()
