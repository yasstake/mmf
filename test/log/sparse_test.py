import unittest
import numpy as np
from collections import deque
from scipy.sparse import *
from scipy import *
from log.dbgen import SparseBoard

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_create_sparse_matrix(self):
        mat = csr_matrix((100, 200000), dtype=float)

        mat2 = csr_matrix((100, 200000), dtype=float)

        np.roll(mat, shift=1)

        print(mat[1, 1])
        print(mat.shape)
        print(mat[90:95, 19999:].shape)

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
