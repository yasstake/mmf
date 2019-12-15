from log.dbgen import SparseMatrix
import unittest


class MyTestCase(unittest.TestCase):
    def test_create(self):
        smatrix = SparseMatrix(5)
        self.assertIsNotNone(smatrix)

    def test_insert_line(self):
        smatrix = SparseMatrix(5)
        smatrix.new_line(100, [1, 2, 3])
        smatrix.new_line(100, [1, 2, 3], False)
        smatrix.new_line(100, [1, 2, 3])

    def test_get_matrix(self):
        smatrix = SparseMatrix(5)
        smatrix.new_line(100, [1, 2, 3])
        smatrix.new_line(100, [1, 2, 3], False)
        smatrix.new_line(100, [1, 2, 3])
        smatrix.new_line(99, [1, 2, 3])
        smatrix.new_line(99, [1, 2, 3], False)
        print(smatrix.get(99, 101))

        smatrix.new_line(99, [1, 2, 3], False)
        print(smatrix.get(99, 101))


if __name__ == '__main__':
    unittest.main()
