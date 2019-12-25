import unittest
from log.constant import ACTION
from log.qvalue import OrderPrices
from log.qvalue import QValue
from log.qvalue import QSequence
from log.qvalue import Q_FAILED_ACTION
from log.qvalue import Q_INVALID_ACTION

from test.log.qvalue_testdata import TEST_PRICE_DATA
from test.log.qvalue_testdata import TEST_PRICE_DATA_BUY_SELL_ONLY


class MyTestCase(unittest.TestCase):
    def test_create_order_price(self):
        order_price = OrderPrices()

        self.assertIsNotNone(order_price)

    def _test_list_data(self):
        for data in TEST_PRICE_DATA:
            print(data)

    def test_set_one_rec(self):
        price = OrderPrices()

        price.set_price_record(TEST_PRICE_DATA[1])

        print(price)

    def test_q_sequence_buy(self):
        q_seq = QSequence(buy_price=TEST_PRICE_DATA[0][1])
        q_seq.set_records(TEST_PRICE_DATA)
        q_seq.update_q()

        number_of_records = len(q_seq.q_values)

        for i in range(number_of_records):
            print(q_seq.q_values[i])

    def test_q_sequence_sell(self):
        q_seq = QSequence(sell_price=TEST_PRICE_DATA[0][1])
        q_seq.set_records(TEST_PRICE_DATA)
        q_seq.update_q()

        number_of_records = len(q_seq.q_values)

        for i in range(number_of_records):
            print(q_seq.q_values[i])

    def test_q_sequence_sell_only(self):
        q_seq = QSequence(sell_price=TEST_PRICE_DATA_BUY_SELL_ONLY[0][1], hold_time_min=7, hold_time_max=10)
        q_seq.set_records(TEST_PRICE_DATA_BUY_SELL_ONLY)
        q_seq.update_q()

        number_of_records = len(q_seq.q_values)

        for i in range(number_of_records):
            print(q_seq.q_values[i])

    def test_q_sequence_buy_only(self):
        q_seq = QSequence(buy_price=TEST_PRICE_DATA_BUY_SELL_ONLY[0][1], hold_time_min=7, hold_time_max=10)
        q_seq.set_records(TEST_PRICE_DATA_BUY_SELL_ONLY)
        q_seq.update_q()

        number_of_records = len(q_seq.q_values)

        for i in range(number_of_records):
            print(q_seq.q_values[i])



if __name__ == '__main__':
    unittest.main()