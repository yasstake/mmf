import unittest
from unittest import TestCase
from log.dbgen import SparseLine


class TestSparseLine(TestCase):
    def test_set_line(self):
        line = SparseLine()
        line.set_line(100, [1, 0, 1])
        self.assertEqual(line.get_line( 99, 100)[0], 0)
        self.assertEqual(line.get_line(100, 101)[0], 1)
        self.assertEqual(line.get_line(101, 102)[0], 0)
        self.assertEqual(line.get_line(102, 103)[0], 1)

        self.assertEqual(line.get_line( 99, 101)[1], 1)
        self.assertEqual(line.get_line(100, 102)[1], 0)
        self.assertEqual(line.get_line(101, 103)[1], 1)
        self.assertEqual(line.get_line(102, 104)[1], 0)

    def test_set_line_r(self):
        line = SparseLine()
        line.set_line(100, [1, 0, 1], False)
        self.assertEqual(line.get_line(99, 100)[0], 0)
        self.assertEqual(line.get_line(100, 101)[0], 1)
        self.assertEqual(line.get_line(101, 102)[0], 0)
        self.assertEqual(line.get_line(102, 103)[0], 0)

        self.assertEqual(line.get_line( 99, 101)[1], 1)
        self.assertEqual(line.get_line(100, 102)[1], 0)
        self.assertEqual(line.get_line(101, 103)[1], 0)
        self.assertEqual(line.get_line(102, 104)[1], 0)

        self.assertEqual(line.get_line(98, 101)[0], 1)
        self.assertEqual(line.get_line(99, 102)[0], 0)
        self.assertEqual(line.get_line(100, 103)[0], 1)
        self.assertEqual(line.get_line(101, 104)[0], 0)

    def test_set_line(self):
        line = SparseLine()
        line.get_line(99, 101)

    def test_get_line(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        r = line.get_line(100, 101)
        print(r)
        print(len(r))
        assert(r[0] == 1)

    def test_get_line_r(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5], False)

        print(line.get_line(90, 101))

        r = line.get_line(100, 101)
        print(r)
        print(len(r))
        self.assertEqual(r[0], 1)

    def test_get_line_1(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])

        r = line.get_line(101, 102)
        print(r)
        print(len(r))
        self.assertEqual(r[0], 2)

    def test_get_line2(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        r = line.get_line(99, 100)
        print(r)
        print(len(r))


    def test_get_line3(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        r = line.get_line(90, 99)
        print(r)
        print(len(r))

    def test_get_line4(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        r = line.get_line(99, 110)
        print(r)
        print(len(r))

    def test_get_line5(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        line.get_line(101, 102)

    def test_get_line6(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        r = line.get_line(101, 110)
        print(r)

    def test_get_line7(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])
        line.get_line(110, 113)


    def test_get_line8(self):
        line = SparseLine()
        line.set_line(100, [1, 2, 3, 4, 5])

        r = line.get_line(98, 100)
        print(r)

        r = line.get_line(99, 101)
        print(r)

        r = line.get_line(100, 102)
        print(r)

        r = line.get_line(101, 103)
        print(r)

        r = line.get_line(102, 104)
        print(r)

        r = line.get_line(103, 105)
        print(r)

        r = line.get_line(104, 106)
        print(r)

        r = line.get_line(105, 107)
        print(r)

        r = line.get_line(106, 108)
        print(r)

        r = line.get_line(107, 109)
        print(r)

        r = line.get_line(108, 110)
        print(r)


    def test_get_line8r(self):
        line = SparseLine()
        line.set_line(104, [1, 2, 3, 4, 5], False)

        r = line.get_line(97, 99)
        print(r)

        r = line.get_line(98, 100)
        print(r)

        r = line.get_line(99, 101)
        print(r)

        r = line.get_line(100, 102)
        print(r)

        r = line.get_line(101, 103)
        print(r)

        r = line.get_line(102, 104)
        print(r)

        r = line.get_line(103, 105)
        print(r)

        r = line.get_line(104, 106)
        print(r)

        r = line.get_line(105, 107)
        print(r)

        r = line.get_line(106, 108)
        print(r)

        r = line.get_line(107, 109)
        print(r)

        r = line.get_line(108, 110)
        print(r)


if __name__ == '__main__':
    unittest.main()
