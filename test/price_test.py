import unittest
from matplotlib import pylab as plt
import numpy as np
from log.price import PriceBoard
from log.logdb import LogDb

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

    def test_save(self):
        board = PriceBoard()

        board.save("/tmp/boarddump.npz")

    def test_latest_time(self):
        db = LogDb()
        db.connect()

        time = db.calc_latest_time()

        print('latest time->', time)




    def test_load_from_db(self):
        t = 1552712195
        board = PriceBoard.load_from_db(t)

        print(board)

        print("sttistics")

        mean, stddev = board.calc_static(board.buy_order+board.sell_order)

        array = board.normalize_array(board.buy_order, mean + stddev)
        plt.imshow(array, vmin=0, vmax=255)
        plt.figure()

        array = board.normalize_array(board.sell_order, mean + stddev)
        plt.imshow(array, vmin=0, vmax=255)
        plt.figure()

        np.savez_compressed('/tmp/compress_sell_order.npz', array)

        mean, stddev = board.calc_static(board.buy_trade + board.sell_trade)

        array = board.normalize_array(board.buy_trade, mean + stddev)
        plt.imshow(array, vmin=0, vmax=100)
        plt.figure()

        array = board.normalize_array(board.sell_trade, mean + stddev)
        plt.imshow(array, vmin=0, vmax=100)
        plt.figure()

        np.savez_compressed('/tmp/compress_sell_trade.npz', array)



#        plt.matshow(board.sell_trade)
#        plt.matshow(board.sell_order)
#        plt.matshow(board.buy_order)
#        print(board.sell_trade)
#        np.save("/tmp/sell.np", board.sell_trade)
#        plt.matshow(board.buy_trade)
        plt.show()

    def test_load_from_db_normalize(self):
        t = 1552712195
        board = PriceBoard.load_from_db(t)

        plt.imshow(board.buy_order, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.sell_order, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.buy_trade, vmin=0, vmax=200)
        plt.figure()

        plt.imshow(board.sell_trade, vmin=0, vmax=200)
        plt.figure()
        plt.show()

    def test_load_from_db_normalize2(self):
        t = 1552712195
        board = PriceBoard.load_from_db(t)

    def test_load_from_db_normalize3(self):
        t = 1552712195
        while True:
            board = PriceBoard.load_from_db(t)
            print("time->", t)
            if not board:
                break
            t = t+1



    def test_calc_variance(self):
        a = np.array([[0.1, 0, 0, 0, 1],
                     [0, 0, 1, 0, 2],
                     [0, 0, 1, 0, 3],
                     [0, 0, 0, 0, 4]])

        print(a)

        non_zero_count = np.nonzero(a)[0].size
        sum_a   = np.sum(a)
        mean = sum_a/non_zero_count

        print("average", sum_a/non_zero_count, sum_a, non_zero_count)

        b = np.square(a)
        square_sum_a = np.sum(b)

        print("square average", square_sum_a/non_zero_count, square_sum_a, non_zero_count)

        s = square_sum_a/non_zero_count - (sum_a/non_zero_count)**2

        # standard dev(non zero factor only)
        print(s**0.5)

        board = PriceBoard()
        mean2, stddev2 = board.calc_static(a)
        self.assertEqual(mean, mean2)
        self.assertEqual(s**0.5, stddev2)

        # clipping 3
        c = np.clip(a, 0, 3)
        print(c)

        d = np.ceil(a)
        print(d)

        e = (a / 3)*255
        f = np.ceil(np.clip(e, 0, 255))
        print(f)

        g = f.astype('uint8')

        print(g)

if __name__ == '__main__':
    unittest.main()
