import sys

from dl import train
from dl import tfrecords
import numpy as np
import log.constant as constant
from log.price import PriceBoardDB

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print('python3.7 predict model tffile')
        exit(-1)

    model = sys.argv[1]
    file  = sys.argv[2]

    train = train.Train()

    train.load_model(model)

    boards, ba, time = tfrecords.read_one_tf_file(file)

    result = train.predict(boards)

    print(result)
    
    for i in range(0,len(ba)):
        print(ba[i], result[i])





