import unittest
from log import bitws
import test.data as data
import json


class MyTestCase(unittest.TestCase):
    def test_ws_create_flag(self):
        bitmex = bitws.BitWs()
        bitmex.create_terminate_flag()

    def test_ws_check_flag(self):
        bitmex = bitws.BitWs()

        if(bitmex.check_terminate_flag()):
            print("terminate flag ok")

    def test_ws_check_flag2(self):
        bitmex = bitws.BitWs()

        bitmex.create_terminate_flag()
        if(bitmex.check_terminate_flag()):
            print("terminate flag ok")


    def test_ws_timestamp(self):
        bitmex = bitws.BitWs()
        print(bitmex.time_stamp_string())

    def test_ws_datestring(self):
        bitmex = bitws.BitWs()
        print(bitmex.date_string())

    def test_ws_decode_encode(self):
        bitmex = bitws.BitWs()

        encodeline = bitws.encode(data.line)
        decodeline = bitws.decode(encodeline)

        print(encodeline)

        print("\n")

        print(decodeline)

        self.assertEqual(data.line, decodeline, "decode error")

    def test_ws_mesage_append(self):
        bitmex = bitws.BitWs()

        bitmex.on_message(None, data.line2)
#        bitmex.dump_message()

#        time.sleep(2)

        bitmex.on_message(None, data.line2)

#        time.sleep(2)
        bitmex.on_message(None, data.line2)

#        bitmex.dump_message()
        bitmex.on_message(None, data.line3)

        bitmex.on_message(None, data.line2)
        bitmex.on_message(None, data.line2)

        bitmex.dump_message()



    def test_ws_connect(self):
        bitmex = bitws.BitWs()
        #        bitmex.start()

        pass

    def test_timestamp(self):
        bitmex = bitws.BitWs()

        print(bitmex.timestamp())

    def dummy(self, time, message):
#        print (time)
        pass

    def test_loader(self):
        loader = bitws.LogLoader()
        loader.load(self.dummy, "./test/test.log")

    def test_loader_message(self):
        loader = bitws.LogLoader()
        loader.on_message(data.line)

    def test_loader_message_partial(self):
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)

    def test_loader_message_update(self):
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.update_message)

    def test_loader_message_delete(self):
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.delete_message)

    def test_loader_message_indert(self):
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)

    def test_loader_message_insert2(self):
        print()
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.partial_message)
        print(loader.get_market_depth())

    def test_loader_message_insert4(self):
        print('insert')
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        print(loader.get_market_depth())

    def test_loader_message_delete1(self):
        print('delete')
        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.delete_message)
        print(loader.get_market_depth())


    def test_loader_message_insert3(self):
        insert_message = """
        {
              "table":"orderBookL2",
              "action":"insert",
              "data":[
                {"symbol":"XBTUSD","id":777,"side":"Buy","size":5}
              ]
        }
        """

        update_message = """
        {
              "table":"orderBookL2",
              "action":"update",
              "data":[
                {"symbol":"XBTUSD","id":777,"side":"Buy","size":50}
              ]
        }
        """

        delete_message = """
        {
              "table":"orderBookL2",
              "action":"delete",
              "data":[
                {"symbol":"XBTUSD","id":777,"side":"Buy","size":5}
              ]
        }
        """


        loader = bitws.LogLoader()
        loader.on_message(data.partial_message)

        loader.on_message(insert_message)
        loader.on_message(update_message)
        loader.on_message(delete_message)

        loader.on_message(data.partial_message)
        loader.on_message(insert_message)
        loader.on_message(update_message)
        loader.on_message(update_message)
        loader.on_message(delete_message)


    def test_strip_message(self):
        bitmex = bitws.BitWs()

        d = json.loads(data.trade_data_long)

        result = bitmex.strip_trade_message(d)
        print(result)




if __name__ == '__main__':
    unittest.main()
