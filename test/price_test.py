import unittest
from matplotlib import pylab as plt
import numpy as np
from log.price import PriceBoard

class MyTestCase(unittest.TestCase):

    def test_set_center_price(self):
        PRICE = 4000.5
        board = PriceBoard()
        board.set_center_price(PRICE)
        price = board.get_center_price()
        self.assertEqual(price, PRICE)

    def test_current_time(self):
        board = PriceBoard()
        board.set_origin_time(1000)
        time = board.get_origin_time()
        self.assertEqual(1000, time)

    def test_get_positoin(self):
        board = PriceBoard()
        board.set_origin_time(1000)
        board.set_center_price(1000)

        x, y = board.get_position(999, 1000.5)
        self.assertEqual(x, 1)
        self.assertEqual(y, 129)

        x, y = board.get_position(1000, 1000)
        self.assertEqual(x,0)
        self.assertEqual(y, 128)


    def test_price_board_init(self):
        board = PriceBoard()
        board.data[1][1][1] = 0

    def test_save(self):
        board = PriceBoard()

        board.save("/tmp/boarddump.npz")

    def test_load_from_db(self):
        t = 1551594701
        board = PriceBoard.load_from_db(t)
        print(board)

        print(board.get_center_price())
        print(board.get_origin_time())

        print(board.sell_trade)
        plt.figure()
        plt.imshow(board.buy_order, vmin=0, vmax=1000000)
#        plt.matshow(board.sell_trade)
#        plt.matshow(board.sell_order)
#        plt.matshow(board.buy_order)
#        print(board.sell_trade)
#        np.save("/tmp/sell.np", board.sell_trade)
#        plt.matshow(board.buy_trade)
        plt.show()

    def test_calc_variance(self):
        a = np.array([[0, 0, 0, 0, 1],
                     [0, 0, 1, 0, 2],
                     [0, 0, 1, 0, 3],
                     [0, 0, 0, 0, 4]])

        print(a)

        non_zero_count = np.nonzero(a)[0].size
        sum_a   = np.sum(a)

        print("average", sum_a/non_zero_count, sum_a, non_zero_count)

        b = np.square(a)
        square_sum_a = np.sum(b)

        print("square average", square_sum_a/non_zero_count, square_sum_a, non_zero_count)

        s = square_sum_a/non_zero_count - (sum_a/non_zero_count)**2

        # standard dev(non zero factor only)
        print(s**0.5)

if __name__ == '__main__':
    unittest.main()
