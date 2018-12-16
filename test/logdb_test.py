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
        log_db.insert(100, order_book)
        log_db.insert(100, order_book)

    def test_message_to_list(self):
        log_db = logdb.LogDb()

        message = json.loads(data.order_book_depth_05)
        list = log_db.message_to_list(message)
        print(list)


if __name__ == '__main__':
    unittest.main()
