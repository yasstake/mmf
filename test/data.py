
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

order_book_depth_05 = """
[{"symbol": "XBTUSD", "id": 17999992000, "side": "Sell", "size": 100, "price": 80}, 
{"symbol": "XBTUSD", "id": 17999993000, "side": "Sell", "size": 20, "price": 79.5}, 
{"symbol": "XBTUSD", "id": 17999994000, "side": "Sell", "size": 10, "price": 80.5}, 
{"symbol": "XBTUSD", "id": 17999994000, "side": "Sell", "size": 10, "price": 100}, 
{"symbol": "XBTUSD", "id": 17999994000, "side": "Sell", "size": 10, "price": 81}, 
{"symbol": "XBTUSD", "id": 17999995000, "side": "Buy", "size": 10, "price": 50}, 
{"symbol": "XBTUSD", "id": 17999996000, "side": "Buy", "size": 20, "price": 49.5}, 
{"symbol": "XBTUSD", "id": 17999997000, "side": "Buy", "size": 100, "price": 51},
{"symbol": "XBTUSD", "id": 17999997000, "side": "Buy", "size": 95, "price": 50.5},
{"symbol": "XBTUSD", "id": 17999997000, "side": "Buy", "size": 98, "price": 10}]
"""

funding_data = """
{
  "table": "funding",
  "action": "partial",
  "keys": [
    "timestamp",
    "symbol"
  ],
  "types": {
    "timestamp": "timestamp",
    "symbol": "symbol",
    "fundingInterval": "timespan",
    "fundingRate": "float",
    "fundingRateDaily": "float"
  },
  "foreignKeys": {
    "symbol": "instrument"
  },
  "attributes": {
    "timestamp": "sorted",
    "symbol": "grouped"
  },
  "filter": {
    "symbol": "XBTUSD"
  },
  "data": [
    {
      "timestamp": "2018-12-20T12:00:00.000Z",
      "symbol": "XBTUSD",
      "fundingInterval": "2000-01-01T08:00:00.000Z",
      "fundingRate": -0.000964,
      "fundingRateDaily": -0.002892
    }
  ]
}
"""


trade_data="""
{"table":"trade","action":"insert","data":[{"timestamp":"2019-01-05T23:01:25.263Z","symbol":"XBTUSD","side":"Sell","size":30,"price":3801.5,"tickDirection":"ZeroMinusTick","trdMatchID":"73960db4-5580-dc30-e281-cd2fdf85a506","grossValue":789150,"homeNotional":0.0078915,"foreignNotional":30}]}
"""

trade_data_long="""
{"table":"trade","action":"insert","data":[{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":6122,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"44e1d575-393e-10a6-af45-085fc7b1f5d7","grossValue":161253480,"homeNotional":1.6125348,"foreignNotional":6122},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":15,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"530b1899-c46c-aac4-5c98-16a09fe2f677","grossValue":395100,"homeNotional":0.003951,"foreignNotional":15},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":2261,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"887534ee-be28-ff36-a8cf-f684b0dfec07","grossValue":59554740,"homeNotional":0.5955474,"foreignNotional":2261},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":15118,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"0840cd4a-f06f-8d02-96ac-07869e114fea","grossValue":398208120,"homeNotional":3.9820812,"foreignNotional":15118},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":90,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"c7e401d6-06ed-95da-b5f4-d5efa937aaa9","grossValue":2370600,"homeNotional":0.023706,"foreignNotional":90},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":150,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"06de04be-2915-598f-cb0f-b146407776df","grossValue":3951000,"homeNotional":0.03951,"foreignNotional":150},{"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":3954,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"56c8462f-a03f-c441-06d9-0f545987400f","grossValue":104148360,"homeNotional":1.0414836,"foreignNotional":3954}]}
"""

trade_data_long2="""
{
    "table":"trade",
    "action":"insert",
    "data":[
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":6122,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"44e1d575-393e-10a6-af45-085fc7b1f5d7","grossValue":161253480,"homeNotional":1.6125348,"foreignNotional":6122},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":15,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"530b1899-c46c-aac4-5c98-16a09fe2f677","grossValue":395100,"homeNotional":0.003951,"foreignNotional":15},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":2261,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"887534ee-be28-ff36-a8cf-f684b0dfec07","grossValue":59554740,"homeNotional":0.5955474,"foreignNotional":2261},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":15118,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"0840cd4a-f06f-8d02-96ac-07869e114fea","grossValue":398208120,"homeNotional":3.9820812,"foreignNotional":15118},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":90,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"c7e401d6-06ed-95da-b5f4-d5efa937aaa9","grossValue":2370600,"homeNotional":0.023706,"foreignNotional":90},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":150,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"06de04be-2915-598f-cb0f-b146407776df","grossValue":3951000,"homeNotional":0.03951,"foreignNotional":150},
    {"timestamp":"2019-01-05T23:29:14.521Z","symbol":"XBTUSD","side":"Sell","size":3954,"price":3796.5,"tickDirection":"ZeroMinusTick","trdMatchID":"56c8462f-a03f-c441-06d9-0f545987400f","grossValue":104148360,"homeNotional":1.0414836,"foreignNotional":3954}]
}
"""

trade_data_buy_partial="""
{"table":"trade","action":"partial","keys":[],"types":{"timestamp":"timestamp","symbol":"symbol","side":"symbol","size":"long","price":"float","tickDirection":"symbol","trdMatchID":"guid","grossValue":"long","homeNotional":"float","foreignNotional":"float"},"foreignKeys":{"symbol":"instrument","side":"side"},"attributes":{"timestamp":"sorted","symbol":"grouped"},"filter":{"symbol":"XBTUSD"},
"data":[{"timestamp":"2019-01-05T23:51:45.711Z","symbol":"XBTUSD","side":"Buy","size":800,"price":3795.5,"tickDirection":"PlusTick","trdMatchID":"dd487e49-9744-cd26-33cd-8a63c6247d89","grossValue":21077600,"homeNotional":0.210776,"foreignNotional":800}
],"TIME":1546699911}
"""

trade_data_buy="""
{"table":"trade","action":"insert","data":[{"timestamp":"2019-01-05T23:51:54.204Z","symbol":"XBTUSD","side":"Buy","size":994,"price":3795.5,"tickDirection":"ZeroPlusTick","trdMatchID":"b7957bd9-1d12-ba95-2fc0-f883a9ed2ef5","grossValue":26188918,"homeNotional":0.26188918,"foreignNotional":994},{"timestamp":"2019-01-05T23:51:54.204Z","symbol":"XBTUSD","side":"Buy","size":2000,"price":3795.5,"tickDirection":"ZeroPlusTick","trdMatchID":"98af4fba-c6b0-b564-1a92-5687adf4151b","grossValue":52694000,"homeNotional":0.52694,"foreignNotional":2000},{"timestamp":"2019-01-05T23:51:54.204Z","symbol":"XBTUSD","side":"Buy","size":2000,"price":3795.5,"tickDirection":"ZeroPlusTick","trdMatchID":"30ecf537-3332-c4d2-cfe2-f4d17988f8d3","grossValue":52694000,"homeNotional":0.52694,"foreignNotional":2000},{"timestamp":"2019-01-05T23:51:54.204Z","symbol":"XBTUSD","side":"Buy","size":6,"price":3795.5,"tickDirection":"ZeroPlusTick","trdMatchID":"1bfa27e7-ebaf-9136-2180-de73a140d684","grossValue":158082,"homeNotional":0.00158082,"foreignNotional":6}],"TIME":1546699914}
"""
