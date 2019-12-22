import unittest
from log.constant import ACTION
from log.logdb import LogDb
from log.qvalue import QValue


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


    def test_crate_db(self):
        db = LogDb()  # create on memory
        db.connect()
        db.create_cursor()
        db.create()
        db.commit()

    def test_crate_db_insert_q(self):
        db = LogDb()  # create on memory
        db.connect()
        db.create_cursor()
        db.create()
        db.commit()

        q = QValue()
        q.q[ACTION.NOP] = 1
        q.q[ACTION.BUY] = 1
        q.q[ACTION.SELL] = 1
        q.q[ACTION.SELL_NOW] = 1
        q.q[ACTION.BUY_NOW] = 1

        db.insert_q(100, 101, ACTION.BUY, q)

    def test_select_db_q(self):
        db = LogDb()  # create on memory
        db.connect()
        db.create_cursor()
        db.create()
        db.commit()

        q = QValue()
        q.q[ACTION.NOP] = 1
        q.q[ACTION.BUY] = 2
        q.q[ACTION.SELL] = 3
        q.q[ACTION.SELL_NOW] = 4
        q.q[ACTION.BUY_NOW] = 5

        db.insert_q(100, 101, ACTION.BUY, q)

        r = db.select_q(100, 101, ACTION.BUY)
        print(r)

    def test_list_db_q(self):
        db = LogDb()  # create on memory
        db.connect()
        db.create_cursor()
        db.create()
        db.commit()

        q = QValue()
        q.q[ACTION.NOP] = 1
        q.q[ACTION.BUY] = 2
        q.q[ACTION.SELL] = 3
        q.q[ACTION.SELL_NOW] = 4
        q.q[ACTION.BUY_NOW] = 5

        db.insert_q(100, 0, ACTION.BUY, q)
        db.insert_q(101, 100, ACTION.BUY, q)
        db.insert_q(102, 100, ACTION.BUY, q)
        db.insert_q(103, 100, ACTION.BUY, q)
        db.insert_q(101, 101, ACTION.BUY, q)
        db.commit()

        r = db.select_q(102, 100, ACTION.BUY)
        print(r)

        r = db.list_q(100, ACTION.BUY)
        print(r)

        for q in r:
            print(q)







if __name__ == '__main__':
    unittest.main()
