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


if __name__ == '__main__':
    unittest.main()
