import unittest

from tensorflow.keras.datasets import mnist
import autokeras as ak


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_minist(self):

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        print(x_train.shape)  # (60000, 28, 28)
        print(y_train.shape)  # (60000,)
        print(y_train[:3])  # array([7, 2, 1], dtype=uint8)

        input_node = ak.ImageInput()
        output_node = ak.ConvBlock()(input_node)
        output_node = ak.DenseBlock()(output_node)
        output_node = ak.ClassificationHead()(output_node)

        clf = ak.AutoModel(inputs=input_node, outputs=output_node, max_trials=10)
        clf.fit(x_train, y_train)


if __name__ == '__main__':
    unittest.main()
