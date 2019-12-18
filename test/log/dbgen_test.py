import unittest
from log.dbgen import Generator

class MyTestCase(unittest.TestCase):
    def test_create_generator(self):
        g = Generator()
        gen1 = g.create(db_name='/bitlog/bitlog20191215.db')

        for i in range(1):
            board = next(gen1)
            print('a', board.current_time, board.center_price)
            a = board.get_std_boards()
            print(a)

            board.save_to_img('/tmp', i)


if __name__ == '__main__':
    unittest.main()
