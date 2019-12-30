import unittest
from log.constant import ACTION
from log.qvalue import OrderPrices
from log.qvalue import QValue
#from log.qvalue import QSequence
from log.qvalue import Q_FAILED_ACTION
from log.qvalue import Q_INVALID_ACTION

from test.log.qvalue_testdata import TEST_PRICE_DATA
from test.log.qvalue_testdata import TEST_PRICE_DATA_BUY_SELL_ONLY
from test.log.qvalue_testdata import TEST_PRICE_DATA_BUY_SELL_ONLY_2


class MyTestCase(unittest.TestCase):
    def test_create_order_price(self):
        order_price = OrderPrices()

        self.assertIsNotNone(order_price)

    def test_set_one_rec(self):
        price = OrderPrices()

        price.set_price_record(TEST_PRICE_DATA[1])
        print(price)

    def test_is_equal_price_value(self):
        price1 = OrderPrices()
        price2 = OrderPrices()

        self.assertEqual(price1.time, price2.time)

        self.assertTrue(price1.is_equal_prices(price2))

        price2.fix_order_buy = 1
        self.assertFalse(price1.is_equal_prices(price2))

    def test_price_constructor(self):
        price_rec = (1, 2, 3, 4, 5, 6, 7)
        price = OrderPrices(price_rec)

        self.assertEqual(price.time, 1)


    def test_accessor(self):
        q = QValue()

        q[ACTION.NOP] = 1
        self.assertEqual(q[ACTION.NOP], 1)

        q[ACTION.BUY] = 2
        self.assertEqual(q[ACTION.BUY], 2)

        q[ACTION.SELL] = 3
        self.assertEqual(q[ACTION.SELL], 3)

    def test_is_same_q(self):
        q1 = QValue()
        q2 = QValue()
        self.assertTrue(q1.is_same_q_exept_nop(q2))

        q1[1] = 1
        q2[1] = 1
        self.assertTrue(q1.is_same_q_exept_nop(q2))

        q1[3] = 4
        q2[3] = 4
        self.assertTrue(q1.is_same_q_exept_nop(q2))

        q1[ACTION.NOP] = 4
        q2[ACTION.NOP] = 1
        self.assertTrue(q1.is_same_q_exept_nop(q2))

        q1 = QValue()
        q2 = QValue()
        q1[1] = 2
        q2[1] = 4
        self.assertFalse(q1.is_same_q_exept_nop(q2))

        q1 = QValue()
        q2 = QValue()
        q1[2] = 2
        q2[2] = 4
        self.assertFalse(q1.is_same_q_exept_nop(q2))

        q1 = QValue()
        q2 = QValue()
        q1[3] = 2
        q2[3] = 4
        self.assertFalse(q1.is_same_q_exept_nop(q2))

        q1 = QValue()
        q2 = QValue()
        q1[4] = 2
        q2[4] = 4
        self.assertFalse(q1.is_same_q_exept_nop(q2))

    def test_best_action(self):
        q = QValue()
        self.assertEqual(q.get_best_action(), 0)

        q[ACTION.BUY] = 1
        self.assertEqual(q.get_best_action(), ACTION.BUY)

        print(q)

if __name__ == '__main__':
    unittest.main()