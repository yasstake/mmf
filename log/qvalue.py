import numpy as np

from log.constant import ACTION

Q_INVALID_ACTION = -10
Q_FAILED_ACTION = -0.1
Q_DISCOUNT_RATE = 0.98
Q_FIRST_DISCOUNT_RATE = 0.9

HOLD_TIME_MAX = 1800
HOLD_TIME_MIN = 120

EXECUTE_TIME_MIN = 30


class OrderPrices:
    def __init__(self, rec=None):
        self.time = None  # 0
        self.market_order_sell = None  # 1
        self.market_order_buy = None  # 2
        self.fix_order_sell = None  # 3
        self.fix_order_sell_time = None  # 4
        self.fix_order_buy = None  # 5
        self.fix_order_buy_time = None  # 6

        if rec:
            self.set_price_record(rec)

    def set_price_record(self, record):
        # time, market_order_sell,market_order_buy,fix_order_sell,fix_order_sell_time,fix_order_buy, fix_order_buy_time
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

    def is_equal_prices(self, price):
        if ((self.market_order_sell != price.market_order_sell) or
            (self.market_order_buy != price.market_order_buy) or
            (self.fix_order_sell != price.fix_order_sell) or
            (self.fix_order_sell_time != price.fix_order_sell_time) or
            (self.fix_order_buy != price.fix_order_buy) or
            (self.fix_order_buy_time != self.fix_order_buy_time)):
            return False
        return True

class QValue:
    def __init__(self, *, time=None, start_time=None, start_action=None, start_price=None):
        self.q = np.zeros((5,))
        self.q[:] = Q_INVALID_ACTION

        # (time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q)
        self.time = time
        self.start_time = start_time
        self.start_action = start_action

        self.order_prices = None

        self.buy_price = None
        self.sell_price = None

        if (start_action == ACTION.BUY) or (start_action == ACTION.BUY_NOW):
            self.buy_price = start_price

        if (start_action == ACTION.SELL) or (start_action == ACTION.SELL_NOW):
            self.sell_price = start_price

    def __getitem__(self, item):
        return self.q[item]

    def __setitem__(self, key, value):
        self.q[key] = value

    def is_same_q_exept_nop(self, q):
        if ((q.q[ACTION.BUY] != self.q[ACTION.BUY]) or
            (q.q[ACTION.SELL] != self.q[ACTION.SELL]) or
            (q.q[ACTION.BUY_NOW] != self.q[ACTION.BUY_NOW]) or
            (q.q[ACTION.SELL_NOW] != self.q[ACTION.SELL_NOW])):
            return False
        else:
            return True

    def set_q_records(self, record):
        # (time, start_time, start_action, nop_q, buy_q, buy_now_q, sell_q, sell_now_q)
        self.time = record[0]
        self.start_time = record[1]
        self.start_action = record[2]
        self.q[ACTION.NOP] = record[3]
        self.q[ACTION.BUY] = record[4]
        self.q[ACTION.BUY_NOW] = record[5]
        self.q[ACTION.SELL] = record[6]
        self.q[ACTION.SELL_NOW] = record[7]

    def set_price_record(self, record):
        # time, market_order_sell,market_order_buy,fix_order_sell,fix_order_sell_time,fix_order_buy, fix_order_buy_time
        self.time = record[0]
        if not self.order_prices:
            self.order_prices = OrderPrices()
        self.order_prices.set_price_record(record)
        self.update_q()

    def update_q(self):
        if self.sell_price:
            if self.order_prices.fix_order_buy:
                q = self.sell_price - self.order_prices.fix_order_buy

                # calc time reduction for q value
                execute_time = self.order_prices.fix_order_buy_time - self.order_prices.time
                self.q[ACTION.BUY] = q * Q_FIRST_DISCOUNT_RATE * (Q_DISCOUNT_RATE ** execute_time)
            else:
                self.q[ACTION.BUY] = Q_FAILED_ACTION

            self.q[ACTION.BUY_NOW] = self.sell_price - self.order_prices.market_order_buy

        if self.buy_price:
            if self.order_prices.fix_order_sell:
                q = self.order_prices.fix_order_sell - self.buy_price

                # calc time reduction for q value
                execute_time = self.order_prices.fix_order_sell_time - self.order_prices.time
                self.q[ACTION.SELL] = q * Q_FIRST_DISCOUNT_RATE * (Q_DISCOUNT_RATE ** execute_time)
            else:
                self.q[ACTION.SELL] = Q_FAILED_ACTION

            self.q[ACTION.SELL_NOW] = self.order_prices.market_order_sell - self.buy_price

    def max_q(self):
        return np.max(self.q)

    def draw_down(self):
        return np.min(self.q)

    def get_best_action(self):
        return np.argmax(self.q)

    def __str__(self):
        return '[{}] NOP[{:+03.5f}] sell[{:+03.5f}] buy[{:+03.5f}] SELL[{:+03.5f}] BUY[{:+03.5f}]'.format(
            self.time, self.q[ACTION.NOP], self.q[ACTION.SELL], self.q[ACTION.BUY], self.q[ACTION.SELL_NOW], self.q[ACTION.BUY_NOW])

'''
class QSequence:
    def __init__(self, *, sell_price=None, buy_price=None, hold_time_max=HOLD_TIME_MAX, hold_time_min=HOLD_TIME_MIN):
        self.q_values = []

        self.action = None

        self.sell_price = sell_price
        self.buy_price = buy_price

        self.hold_time_max = hold_time_max
        self.hold_time_min = hold_time_min

        self.start_time = 0

        self.q = 0

    def _set_records(self, records):
        for r in records:
            q_value = QValue()
            q_value.set_price_record(r)

            print('sell-by price', self.buy_price, self.sell_price, r)

            q_value.buy_price = self.buy_price
            q_value.sell_price = self.sell_price
            q_value.update_q()

            self.q_values.append(q_value)

    def set_records(self, records):
        q_sequence = []
        seq_position = 0

        max_q = -9999

        for r in records:
            q_value = QValue()
            q_value.set_price_record(r)

            q_value.buy_price = self.buy_price
            q_value.sell_price = self.sell_price
            q_value.update_q()

            # todo add max draw down
            if max_q < q_value.max_q():
                max_q = q_value.max_q()
                q_sequence.append(q_value)
                self.q_values.extend(q_sequence)
                q_sequence = []
            elif len(self.q_values) < self.hold_time_min:
                q_sequence.append(q_value)
            else:
                self.q_values.extend(q_sequence)
                break

            if self.hold_time_max < seq_position:
                break
            seq_position += 1

    def update_q(self):
        next_q_value = 0

        for r in reversed(self.q_values):
            r.q[ACTION.NOP] = next_q_value
            max_q = r.max_q()
            next_q_value == max_q * Q_DISCOUNT_RATE

        if 0 < len(self.q_values):
            self.q = self.q_values[0].max_q()

    def calc_q_sequence(self, *, start_time, action, start_price, records):
        self.start_time = start_time
        self.action = action

        if (action == ACTION.SELL) or (action == ACTION.SELL_NOW):
            self.sell_price = start_price
            self.buy_price = 0
        elif (action == ACTION.BUY) or (action == ACTION.BUY_NOW):
            self.sell_price = 0
            self.buy_price = start_price

        self.set_records(records)
        self.update_q()

    def dump_q(self):
        for q in self.q_values:
            print(self.start_time, q.order_prices.time, self.action, q)
'''
