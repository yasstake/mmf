from dl.train import Train
import sys


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print('python3.7 train.py trainpattern testpattern')
    
    train_pattern = sys.argv[1] + '/*.tfrecords'
    test_pattern = sys.argv[2] +  '/*.tfrecords'

    train = Train()
    train.create_model()
#    train.do_train('/tmp/2019/T/*.tfrecords', '/tmp/2019/T/*.tfrecords')
    train.do_train(train_pattern, test_pattern)

#    train.do_train(('/tmp/2019/03/17/*.tfrecords', '/tmp/2019/03/18/*.tfrecords',
#                    '/tmp/2019/03/19/*.tfrecords', '/tmp/2019/03/20/*.tfrecords'),
#                   '/tmp/2019/03/21/*.tfrecords')


#    train.do_train('gs://bitboard/2019/03/21/*.tfrecords', 'gs://bitboard/2019/03/22/*.tfrecords')




