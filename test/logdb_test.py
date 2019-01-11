import unittest
from log import logdb
import test.data as data
import json


class LogDbTest(unittest.TestCase):

    def test_create(self):
        log_db = logdb.LogDb()

        log_db.connect()
        log_db.create()

    def test_load(self):
        log_db = logdb.LogDb()
        log_db.connect()
        log_db.create()

        order_book = json.loads(data.order_book_depth)
        log_db.insert_order_book(100, order_book)
        log_db.insert_order_book(100, order_book)

    def test_message_to_list(self):
        log_db = logdb.LogDb()

        message = json.loads(data.order_book_depth_05)
        list = log_db.message_to_list(message)
        print(list)



    def test_message_to_list_zip(self):
        log_db = logdb.LogDb()

        message = [1000,2,3,400]

        m2 = log_db.list_to_zip_string(message)

        m3 = log_db.zip_string_to_list(m2)
        print (m2)
        print ('\n')
        print (m3)
        assert(message == m3)








if __name__ == '__main__':
    unittest.main()
