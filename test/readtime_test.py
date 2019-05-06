import unittest

from log.encoder import decode
from log.realtime import MemoryLoader
from test import data


class RealTimeTestCase(unittest.TestCase):

    def test_create(self):
        loader = MemoryLoader()

    def test_load_line(self):
        loader = MemoryLoader()

        loader.load_line(data.partial_message)
        loader.load_line(data.insert_message)
        loader.load_line(data.insert_message)
        loader.load_line(data.partial_message)


    def test_load_file(self):
        loader = MemoryLoader()

        for line in open('./data/bit.log','r'):
            loader.load_line(decode(line))


if __name__ == '__main__':
    unittest.main()
