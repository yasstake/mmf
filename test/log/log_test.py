import numpy as np
import unittest

from log.logdb import LogDb

class MyTestCase(unittest.TestCase):

    def test_encode_list(self):
        array = np.array([1, 2], dtype=np.float)
        data = array.data
        print(data)

        print(len(data))

        array2 = np.frombuffer(data, dtype=np.float)
        print(array2)
        pass

    def test_decode_list(self):
        db = LogDb()

        l = [99991, 99992, 99993, 99994, 99995, 99991, 99992, 99993, 99994, 99995, 99991, 99992, 99993, 99994, 99995]

        print(l)
        print(len(l))

        b = db.list_to_bin(l)

        print(b)
        print('compressize=>', len(b))

        l2 = db.bin_to_list(b)

        print(l2)
        print(len(l2))

        zs = db.list_to_zip_string(l)
        print(len(zs))
        print(zs)

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
