import numpy as np

from log.constant import ACTION

Q_INVALID_ACTION = -0.1
Q_FAILED_ACTION = -0.0001
Q_DISCOUNT_RATE = 0.995
Q_FIRST_DISCOUNT_RATE = 0.7

HOLD_TIME_MAX = 3600
HOLD_TIME_MIN = 60


class OrderPrices:
    def __init__(self):
        self.time = None  # 0
        self.market_order_sell = None  # 1
        self.market_order_buy = None  # 2
        self.fix_order_sell = None  # 3
        self.fix_order_sell_time = None  # 4
        self.fix_order_buy = None  # 5
        self.fix_order_buy_time = None  # 6

    def set_price_record(self, record):
        self.time = record[0]
        self.market_order_sell = record[1]
        self.market_order_buy = record[2]
        self.fix_order_sell = record[3]
        self.fix_order_sell_time = record[4]
        self.fix_order_buy = record[5]
        self.fix_order_buy_time = record[6]

    def __str__(self):
        return 'T({}) mos({}) mob({}) fos({}[{}]) fob({}[{}])'.format(
            self.time, self.market_order_sell, self.market_order_buy,
            self.fix_order_sell, self.fix_order_sell_time, self.fix_order_buy,
            self.fix_order_buy_time
        )


class QValue:
    def __init__(self):
        self.q = np.zeros((5,))
        self.order_prices = None

    def set_price_record(self, record):
        self.order_prices = OrderPrices()
        self.order_prices.set_price_record(record)

    def set_sell_price(self, price):
        if not price:
            return

        self.q[ACTION.SELL] = Q_INVALID_ACTION
        self.q[ACTION.SELL_NOW] = Q_INVALID_ACTION

        if self.order_prices.fix_order_buy:
            self.q[ACTION.BUY] = price - self.order_prices.fix_order_buy
        else:
            self.q[ACTION.BUY] = Q_FAILED_ACTION

        if self.order_prices.market_order_buy:
            self.q[ACTION.BUY_NOW] = price - self.order_prices.market_order_buy
        else:
            self.q[ACTION.BUY_NOW] = Q_FAILED_ACTION

    def set_buy_price(self, price):
        if not price:
            return

        if self.order_prices.fix_order_sell:
            self.q[ACTION.SELL] = self.order_prices.fix_order_sell - price
        else:
            self.q[ACTION.SELL] = Q_FAILED_ACTION

        if self.order_prices.market_order_sell:
            self.q[ACTION.SELL_NOW] = self.order_prices.market_order_sell - price
        else:
            self.q[ACTION.SELL_NOW] = Q_FAILED_ACTION

        self.q[ACTION.BUY] = Q_INVALID_ACTION
        self.q[ACTION.BUY_NOW] = Q_INVALID_ACTION

    def get_max_q(self):
        return np.max(self.q)

    def __str__(self):
        return 'NOP[{}] sell[{}] buy[{}] SELL[{}] BUY[{}]'.format(
            self.q[ACTION.NOP], self.q[ACTION.SELL], self.q[ACTION.BUY], self.q[ACTION.SELL_NOW], self.q[ACTION.BUY_NOW])


class QSequence:
    def __init__(self, *, sell_price=None, buy_price=None, hold_time_max=HOLD_TIME_MAX, hold_time_min=HOLD_TIME_MIN):
        self.q_values = []

        self.action = None

        self.sell_price = sell_price
        self.buy_price = buy_price

        self.max_q = 0
        self.hold_time_max = hold_time_max
        self.hold_time_min = hold_time_min

    def set_records(self, records):
        q_sequence = []

        for r in records:
            q_value = QValue()
            q_value.set_price_record(r)
            q_value.set_buy_price(self.buy_price)
            q_value.set_sell_price(self.sell_price)

            if self.max_q < q_value.get_max_q():
                self.max_q = q_value.get_max_q()
                q_sequence.append(q_value)
                self.q_values.extend(q_sequence)
                q_sequence = []
            elif len(self.q_values) + len(q_sequence) < HOLD_TIME_MIN:
                q_sequence.append(q_value)

    def update_q(self):
        next_q_value = 0

        for r in reversed(self.q_values):
            r.q[ACTION.NOP] = next_q_value
            max_q = r.get_max_q()

            if next_q_value == max_q:
                next_q_value = max_q * Q_DISCOUNT_RATE
            else:
                next_q_value = max_q * Q_FIRST_DISCOUNT_RATE

    def calc_q_sequence(self, start_time, action):
        # TODO not implemenetd
        pass
