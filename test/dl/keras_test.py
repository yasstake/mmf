import unittest

from log.constant import *

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.layers import InputLayer




class MyTestCase(unittest.TestCase):
    def test_simple_sequential_mode(self):

        model = Sequential()

        model.add(
            Dense(
                units=64,
                input_shape=(BOARD_TIME_WIDTH, BOARD_WIDTH, NUMBER_OF_LAYERS),
                activation='relu'
            )
        )

        model.add(
            Dense(
                units = 5,
                activation='softmax'
            )
        )


if __name__ == '__main__':
    unittest.main()
