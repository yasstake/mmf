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

#train.do_train(train_pattern, test_pattern)

#    train.do_train(('/bitlog/BALANCED/20190320/*.tfrecords', '/bitlog/BALANCED/20190321/*.tfrecords',
#                    '/bitlog/BALANCED/20190322/*.tfrecords', 
#                    '/bitlog/BALANCED/20190323/*.tfrecords',
#                    '/bitlog/BALANCED/20190325/*.tfrecords'), '/bitlog/2019/03/29/*.tfrecords')


#    train.do_train('gs://bitboard/2019/03/21/*.tfrecords', 'gs://bitboard/2019/03/22/*.tfrecords')

    train.do_train(('/bitlog/2019/03/20/*.tfrecords',
                    '/bitlog/2019/03/21/*.tfrecords',
                    '/bitlog/2019/03/22/*.tfrecords',
                    '/bitlog/2019/03/23/*.tfrecords',
                    '/bitlog/2019/03/24/*.tfrecords',
                    '/bitlog/2019/03/25/*.tfrecords',                                         
                    ), '/bitlog/2019/03/29/*.tfrecords')



