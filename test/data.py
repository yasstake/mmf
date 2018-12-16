
line = """
{"table":"orderBookL2","action":"update","data":[{"symbol":"XBTUSD","id":8799358600,"side":"Sell","size":458134},{"symbol":"XBTUSD","id":8799358700,"side":"Sell","size":1132499},{"symbol":"XBTUSD","id":8799358900,"side":"Sell","size":1668642},{"symbol":"XBTUSD","id":8799359000,"side":"Sell","size":961890},{"symbol":"XBTUSD","id":8799359200,"side":"Sell","size":359970},{"symbol":"XBTUSD","id":8799359300,"side":"Sell","size":676368},{"symbol":"XBTUSD","id":8799359500,"side":"Sell","size":641352},{"symbol":"XBTUSD","id":8799359550,"side":"Sell","size":213955},{"symbol":"XBTUSD","id":8799359850,"side":"Buy","size":214899},{"symbol":"XBTUSD","id":8799359900,"side":"Buy","size":144012},{"symbol":"XBTUSD","id":8799360150,"side":"Buy","size":91487},{"symbol":"XBTUSD","id":8799360450,"side":"Buy","size":415735},{"symbol":"XBTUSD","id":8799360750,"side":"Buy","size":548556}]}
"""

line2 = """
{"table":"orderBookL2","action":"update","data":[{"symbol":"XBTUSD","id":8799358600,"side":"Sell","size":458134}]}
"""

line3 = """
{"table":"orderBookL2","action":"delete","data":[{"symbol":"XBTUSD","id":8799358600,"side":"Sell","size":458134}]}
"""

partial_message = """
{
      "table":"orderBookL2",
      "keys":["symbol","id","side"],
      "types":{"id":"long","price":"float","side":"symbol","size":"long","symbol":"symbol"},
      "foreignKeys":{"side":"side","symbol":"instrument"},
      "attributes":{"id":"sorted","symbol":"grouped"},
      "action":"partial",
      "data":[
        {"symbol":"XBTUSD","id":17999992000,"side":"Sell","size":100,"price":80},
        {"symbol":"XBTUSD","id":17999993000,"side":"Sell","size":20,"price":70},
        {"symbol":"XBTUSD","id":17999994000,"side":"Sell","size":10,"price":60},
        {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":10,"price":50},
        {"symbol":"XBTUSD","id":17999996000,"side":"Buy","size":20,"price":40},
        {"symbol":"XBTUSD","id":17999997000,"side":"Buy","size":100,"price":30}
      ]
}
"""

update_message = """
{
      "table":"orderBookL2",
      "action":"update",
      "data":[
        {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":5}
      ]
}
"""

delete_message = """
{
      "table":"orderBookL2",
      "action":"delete",
      "data":[
        {"symbol":"XBTUSD","id":17999995000,"side":"Buy"}
      ]
}
"""

insert_message = """
{
      "table":"orderBookL2",
      "action":"insert",
      "data":[
        {"symbol":"XBTUSD","id":17999995500,"side":"Buy","size":10,"price":45}
      ]
}
"""

order_book_depth = """
[{"symbol": "XBTUSD", "id": 17999992000, "side": "Sell", "size": 100, "price": 80}, {"symbol": "XBTUSD", "id": 17999993000, "side": "Sell", "size": 20, "price": 70}, {"symbol": "XBTUSD", "id": 17999994000, "side": "Sell", "size": 10, "price": 60}, {"symbol": "XBTUSD", "id": 17999995000, "side": "Buy", "size": 10, "price": 50}, {"symbol": "XBTUSD", "id": 17999996000, "side": "Buy", "size": 20, "price": 40}, {"symbol": "XBTUSD", "id": 17999997000, "side": "Buy", "size": 100, "price": 30}]
"""