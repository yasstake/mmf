from collections import deque
from collections import namedtuple

from log.loader import LogLoader

OrderBook  = namedtuple('OrderBook', ['time', 'sell_min', 'sell_vol', 'sell_list', 'buy_max', 'buy_vol', 'buy_list'])
Trade  = namedtuple('Trade', ['time', 'price', 'volume'])

class MemoryLoader:
    def __init__(self):
        self.log_loader = LogLoader(self.order_book_tick,  self.trade_tick, self.funding_tick)
        self.order_book = deque()
        self.sell_trade = deque()
        self.buy_trade = deque()
        self.last_time = 0

    def order_book_tick(self, time_stamp, order_book):
        sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list = LogLoader.message_to_list(order_book)

        self.order_book.append(OrderBook(time_stamp, sell_min, sell_vol, sell_list, buy_max, buy_vol, buy_list))

        self.new_tick(time_stamp)

    def trade_tick(self, time_stamp, trade_buy, trade_sell):
#        for trade in trade_buy:
#            self.buy_trade.append(Trade(trade['price'], trade['volume']))
        print(time_stamp, trade_buy, trade_sell)

    def funding_tick(self, time_stamp, funding):
        print(time_stamp, funding)

    def new_tick(self, time):
        if self.last_time + 1 != time:
            #fillout
            pass



    def load_line(self, line):
        self.log_loader.load_line(line)

