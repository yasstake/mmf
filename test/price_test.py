import unittest
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
        board = PriceBoard.load_from_db(1551187602)
        print(board)

if __name__ == '__main__':
    unittest.main()
