import sys

from dl import train
from dl import tfrecords
import numpy as np
from sklearn.metrics import confusion_matrix

import log.constant as constant
from log.price import PriceBoardDB

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print('python3.7 predict.py model tffile')
        exit(-1)

    model = sys.argv[1]
    file  = sys.argv[2]

    train = train.Train()

    train.load_model(model)

    boards, ba, time = tfrecords.read_one_tf_file(file)

    result = train.predict(boards)

    print(result)
    print(ba)



    print('----> prediction ---->')
    score = train.predict_summary(answer, forcast)

    print(score)


    score = np.zeros((5, 5))
    for i in range(0,len(ba)):
        score[np.argmax(ba[i])][np.argmax(result[i])] += 1
    print('----> prediction ---->')

    print(score)



    



