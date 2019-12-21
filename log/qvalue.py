import numpy as np

from log.constant import ACTION


Q_INVALID_ACTION = -0.1
Q_FAILED_ACTION = -0.0001
Q_DISCOUNT_RATE = 0.995
Q_FIRST_DISCOUNT_RATE = 0.7


class OrderPrices:
    def __init__(self):
        self.time = None  # 0
        self.market_order_sell = None  # 1
        self.market_order_buy = None  # 2
        self.fix_order_sell = None  # 3
        self.fix_order_sell_time = None  # 4
        self.fix_order_buy = None  # 5
        self.fix_order_buy_time = None  # 6

    def set_record(self, record):
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
    def __init__(self, record):
        self.q = np.zeros((5,))
        self.order_prices = OrderPrices()
        self.set_record(record)

    def set_record(self, record):
        self.order_prices.set_record(record)

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
    def __init__(self):
        self.buy_price = None
        self.sell_price = None
        self.q_values = []

    def set_records(self, records):
        for r in records:
            self.q_values.append(QValue(r))

    def update_q(self):
        next_q_value = 0

        for r in reversed(self.q_values):
            r.set_buy_price(self.buy_price)
            r.set_sell_price(self.sell_price)

            r.q[ACTION.NOP] = next_q_value
            maxq = r.get_max_q()

            if next_q_value == maxq:
                next_q_value = maxq * Q_DISCOUNT_RATE
            else:
                next_q_value = maxq * Q_FIRST_DISCOUNT_RATE


