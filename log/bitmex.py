from bitmex_websocket import BitMEXWebsocket


ws = BitMEXWebsocket(endpoint="wss://www.bitmex.com/realtime", symbol="XBTUSD")


order_book = ws.market_depth()

buy_order = {};
sell_order = {};

sorted_order = sorted(order_book, key=lambda order: order['price'])


print("\n")

for order in sorted_order:
    side = order['side']
    size = order['size']
    price = order['price']

    print(side, price, size)
    if(side == "Buy"):
        buy_order[price] = size
    elif(side == "Sell"):
        sell_order[price] = size



print("\n")
print(buy_order.keys())
print("\n")
print(buy_order)

#while(ws.ws.sock.connected):
#    order_book = ws.market_depth()
#    sleep(1)
#    print(ws.market_depth())

