import scipy
import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_class_weight(self):
        pass


if __name__ == '__main__':
    unittest.main()
