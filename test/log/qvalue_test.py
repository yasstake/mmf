import unittest
from log.constant import ACTION
from log.qvalue import OrderPrices
from log.qvalue import QValue
from log.qvalue import QSequence
from log.qvalue import Q_FAILED_ACTION
from log.qvalue import Q_INVALID_ACTION

from test.log.qvalue_testdata import TEST_PRICE_DATA


class MyTestCase(unittest.TestCase):
    def test_create_order_price(self):
        order_price = OrderPrices()

        self.assertIsNotNone(order_price)

    def _test_list_data(self):
        for data in TEST_PRICE_DATA:
            print(data)

    def test_set_one_rec(self):
        price = OrderPrices()

        price.set_record(TEST_PRICE_DATA[1])

        print(price)

    def test_q_value_buy(self):
        qvalue = QValue(TEST_PRICE_DATA[1])
        buy_price = TEST_PRICE_DATA[0][1]
        qvalue.set_buy_price(buy_price)
        print(buy_price)
        print(qvalue)
        print(qvalue.order_prices)

        self.assertEqual(qvalue.q[ACTION.BUY], Q_INVALID_ACTION)
        self.assertEqual(qvalue.q[ACTION.BUY_NOW], Q_INVALID_ACTION)


    def test_q_value_buy(self):
        qvalue = QValue(TEST_PRICE_DATA[1])
        buy_price = TEST_PRICE_DATA[0][1]
        qvalue.set_buy_price(buy_price)

        print(qvalue)
        print(qvalue.get_max_q())






    def test_q_value_sell(self):
        qvalue = QValue(TEST_PRICE_DATA[1])
        sell_price = TEST_PRICE_DATA[0][2]
        qvalue.set_sell_price(sell_price)
        print(sell_price)
        print(qvalue)
        print(qvalue.order_prices)

        self.assertEqual(qvalue.q[ACTION.SELL], Q_INVALID_ACTION)
        self.assertEqual(qvalue.q[ACTION.SELL_NOW], Q_INVALID_ACTION)

    def test_q_sequence(self):
        q_seq = QSequence()
        q_seq.set_records(TEST_PRICE_DATA)

        q_seq.buy_price = TEST_PRICE_DATA[0][1]
        q_seq.update_q()

        number_of_records = len(q_seq.q_values)

        for i in range(number_of_records):
            print(q_seq.q_values[i])




if __name__ == '__main__':
    unittest.main()