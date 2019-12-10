import unittest
import numpy as np
from collections import deque
from scipy.sparse import *
from scipy import *
from scipy.ndimage.interpolation import shift
from log.dbgen import SparseBoard

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



    def test_generate_sparse_board(self):
        board = SparseBoard()

    def test_generate_sparse_board_addline(self):
        board = SparseBoard()

        b = np.zeros((5, 5), dtype=float)
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 0, [1, 2])
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 0.5, [3, 4])
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 1, [5, 6])
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 1, [5, 6])
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 1, [5, 6])
        print(b)
        b = board._roll(b)
        board._add_order_line(b, 1, [5, 6], False)
        print(b)

    def test_generate_board_line(self):
        board = SparseBoard()
#        board.add_order_line(, 0, [1, 2, 3])

        b = board.get_board()
        print(b)

if __name__ == '__main__':
    unittest.main()
