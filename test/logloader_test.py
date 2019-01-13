import unittest
import test.data as data
from log.loader import LogLoader

class MyTestCase(unittest.TestCase):
    def test_loader(self):
        loader = LogLoader()
        loader.load("./test/test.log")

    def test_loader_message(self):
        loader = LogLoader()
        loader.on_message(data.line)

    def test_loader_message_partial(self):
        loader = LogLoader()
        loader.on_message(data.partial_message)

    def test_loader_message_update(self):
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.update_message)

    def test_loader_message_delete(self):
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.delete_message)

    def test_loader_message_indert(self):
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)

    def test_loader_message_insert2(self):
        print()
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.partial_message)
        print(loader.get_market_depth())

    def test_loader_message_insert4(self):
        print('insert')
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        print(loader.get_market_depth())

    def test_loader_message_delete1(self):
        print('delete')
        loader = LogLoader()
        loader.on_message(data.partial_message)
        loader.on_message(data.insert_message)
        loader.on_message(data.delete_message)
        print(loader.get_market_depth())


if __name__ == '__main__':
    unittest.main()
