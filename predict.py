from dl import train
import numpy as np
import log.constant as constant
from log.price import PriceBoardDB

if __name__ == '__main__':
    print('predict')

    train = train.Train()

    train.load_model('/tmp/bitmodel.h5')

    board1 = PriceBoardDB.load_from_db(1553301418).get_board()
    board2 = PriceBoardDB.load_from_db(1553300968).get_board()

    #array = np.random.random((1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH))

    array = np.stack([board1, board1])

    result = train.predict(array)
    print(result)

    #print(board1.best_action)
    #print(board2.best_action)



