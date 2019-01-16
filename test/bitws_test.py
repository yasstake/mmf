import unittest
from log import bitws
from log import encoder
import test.data as data
import json
from log import loader
from log.timeutil import *

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


    def test_ws_decode_encode(self):
        bitmex = bitws.BitWs()

        encodeline = encoder.encode(data.line)
        decodeline = encoder.decode(encodeline)

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

        load = loader.LogLoader()
        load.on_message(data.partial_message)

        load.on_message(insert_message)
        load.on_message(update_message)
        load.on_message(delete_message)

        load.on_message(data.partial_message)
        load.on_message(insert_message)
        load.on_message(update_message)
        load.on_message(update_message)
        load.on_message(delete_message)


    def test_strip_message(self):
        bitmex = bitws.BitWs()

        d = json.loads(data.trade_data_long)

        result = bitmex.strip_trade_message(d)
        print(result)

    def test_time_sec(self):
        bitmex = bitws.BitWs()
        iso_string = "2019-01-12T15:12:51.313Z"
        sec = time_sec(iso_string)

        iso_string2 = "2019-01-12T15:12:01.313Z"
        sec2 = time_sec(iso_string2)

        assert(sec == sec2 + 50)


if __name__ == '__main__':
    unittest.main()
