import unittest
import numpy as np
from collections import deque
from scipy.sparse import *
from scipy import *
from scipy.ndimage.interpolation import shift
from log.constant import BOARD_WIDTH
from log.dbgen import SparseMatrix
from log.dbgen import PriceBoard


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_create_sparse_matrix(self):
        mat = lil_matrix((10, 200000), dtype=float)

        mat[1, 10000] = 1
        mat[1, 10003] = 3
        print(mat.data)
        print(mat.rows)

        print(mat)

        # shift array
        print(mat.data[:1])
        mat.data[-1] = list()
        mat.data = np.append(mat.data[-1:], mat.data[0:-1])

        mat.rows[-1] = list()
        mat.rows = np.append(mat.rows[-1:], mat.rows[0:-1])

        print(mat.data)
        print(mat.rows)

        print(mat)

        print('----')





if __name__ == '__main__':
    unittest.main()
