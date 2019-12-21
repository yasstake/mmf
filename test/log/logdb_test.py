import unittest
from log.logdb import LogDb


class MyTestCase(unittest.TestCase):

    def test_list_price_info(self):
        db = LogDb(db_name='/bitlog/bitlog.db')
        db.connect()

        time = None                 # 0
        market_order_sell = None    # 1
        market_order_buy = None     # 2
        fix_order_sell = None       # 3
        fix_order_sell_time = None  # 4
        fix_order_buy = None        # 5
        fix_order_buy_time = None   # 6

        line_count = 0
        block_count = 0

        for line in db.list_price_():
            if ((line[1] != market_order_sell)
                    or (line[2] != market_order_buy)
                    or (line[3] != fix_order_sell)
                    or (line[5] != fix_order_buy)):
                print(line, ',')
                block_count += 1

            line_count += 1
            time, market_order_sell, market_order_buy, fix_order_sell, fix_order_sell_time, fix_order_buy, fix_order_buy_time = line

        print('line', line_count, 'block_count', block_count)

if __name__ == '__main__':
    unittest.main()
