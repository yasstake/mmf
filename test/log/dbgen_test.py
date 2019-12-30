import unittest
from log.dbgen import Generator

class MyTestCase(unittest.TestCase):
    def test_create_generator(self):
        g = Generator()
        gen1 = g.create(db_name='/bitlog/bitlog.db')

        for i in range(1):
            board = next(gen1)
            print('a', board.current_time, board.center_price)
            a = board.get_std_boards()
            print(a)

            board.save_to_img('/tmp', i)


    def test_create_generator2(self):
        g = Generator()
        gen1 = g.create(db_name='/bitlog/bitlog.db')

        for i in range(100):
            board = next(gen1)
            print(board.current_time, board.center_price)
            print(board.q_value)


if __name__ == '__main__':
    unittest.main()
