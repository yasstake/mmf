import unittest
from log.price import PriceLine
from log.price import PriceBoard

class MyTestCase(unittest.TestCase):
    def set_hash(self):
        line = PriceLine()

        hash = {10:10, 12:11, 13:9}
        line.sethash(hash)
        print (line.getline())

    def test_set_center_price(self):
        PRICE = 4000.5
        board = PriceBoard()
        board.set_center_price(PRICE)
        price = board.get_center_price()
        assert(price == PRICE)

    def test_current_time(self):
        board = PriceBoard()
        board.set_origin_time(1000)
        time = board.get_origin_time()
        assert(1000 == time)

    def test_get_positoin(self):
        board = PriceBoard()
        board.set_origin_time(1000)
        board.set_center_price(1000)

        x, y = board.get_position(999, 1000.5)
        print(x, y)

        x, y = board.get_position(1000, 1000)
        print(x, y)


    def test_price_board_init(self):
        board = PriceBoard()
        board.data[1][1][1] = 0

    def test_save(self):
        board = PriceBoard()

        board.save("/tmp/boarddump.npz")

if __name__ == '__main__':
    unittest.main()
