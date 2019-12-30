import unittest
from log.constant import ACTION
from log.logdb import LogDb
from log.qvalue import OrderPrices
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

        org_price = OrderPrices()

        line_count = 0
        block_count = 0

        for line in db.list_price():
            price = OrderPrices()
            price.set_price_record(line)

            if (
                (price.market_order_sell != org_price.market_order_sell)
                or (price.market_order_buy != org_price.market_order_buy)
                or (price.fix_order_sell != org_price.fix_order_sell)
                or (price.fix_order_buy != org_price.fix_order_buy)):

                print(price, ',')
                block_count += 1

            line_count += 1
            org_price.set_price_record(line)

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

    def test_list_update_q(self):
        db = LogDb('/bitlog/bitlog.db')  # create on memory
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

        db.insert_updated_q()


    def test_create_q_values(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()
        db.create()

        start, end = db.get_db_info()
        print('start/end', start, end)

        price = db.list_price(start_time=start, end_time=start + 150)
        print(len(price))

        q_seq = db.create_q_sequence(start_time=start, action=ACTION.SELL, start_price=7245)
        q_seq.dump_q()


    def test_create_q_and_insert(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()
        db.create()

        start, end = db.get_db_info()
        print('start/end', start, end)

        db.insert_updated_q()

    def test_select_q(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()
        db.create()

        start, end = db.get_db_info()

        #q = db.select_q_values(start, ACTION.NOP)
        #q = db.select_q_values(start, ACTION.BUY)
        #q = db.select_q_values(start, ACTION.BUY_NOW)
        q = db.select_q_values(start, ACTION.SELL)
        print(q)
        q = db.select_q_values(start, ACTION.SELL_NOW)
        print(q)


    def test_update_q_on_nop(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        db.update_q_on_nop()


    def test_update_all_q_values(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        db.update_all_q()

        db.commit()

    def test_select_hi_price(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        start, _ = db.get_db_info()
        p = db.select_center_price(start)
        r = db.select_highest_price_time(start)
        print(start, p, r)

        start += 500
        p = db.select_center_price(start)
        r = db.select_highest_price_time(start)
        print(start, p, r)

        start += 500
        p = db.select_center_price(start)
        r = db.select_highest_price_time(start)
        print(start, p, r)

        start += 500
        p = db.select_center_price(start)
        r = db.select_highest_price_time(start)
        print(start, p, r)

        start += 5000
        p = db.select_center_price(start)
        r = db.select_highest_price_time(start)
        print(start, p, r)


    def test_create_high_q_sequcen(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        start, _ = db.get_db_info()

        start_price = 7000
        action = ACTION.BUY

        db.create_q_sequence(start_time=start, action=action, start_price=start_price)


    def test_create_low_q_sequcen(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        start, _ = db.get_db_info()

        start_price = 7220
        action = ACTION.SELL

        db.create_q_sequence(start_time=start, action=action, start_price=start_price)




    def test_select_low_price(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        start, _ = db.get_db_info()
        r = db.select_lowest_price_time(start)

        print(start, r)


    def test_select_q(self):
        db = LogDb('/bitlog/bitlog.db')
        db.connect()
        db.create_cursor()

        q = db.select_q(0, 0, 0)
        print(q)

        q = db.select_q(0, 0, 1)
        print(q)

        q = db.select_q(1575501187, 1575501187, 2)
        print(q)

        q = db.select_q(1575542888, 1575542888, 1)
        print(q)
        q = db.select_q(1575542888, 1575542888, 2)
        print(q)
        q = db.select_q(1575542888, 1575542888, 3)
        print(q)
        q = db.select_q(1575542888, 1575542888, 4)
        print(q)





if __name__ == '__main__':
    unittest.main()
