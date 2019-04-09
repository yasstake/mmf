from dl.train import Train
import sys


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print('python3.7 train.py trainpattern testpattern')
    
    train_pattern = sys.argv[1]
    test_pattern = sys.argv[2]

    train_pattern = (
        '/tmp/2019/03/22/*.tfrecords',
        '/tmp/2019/03/23/*.tfrecords',
        '/tmp/2019/03/24/*.tfrecords'
        '/tmp/2019/03/25/*.tfrecords'
        '/tmp/2019/03/26/*.tfrecords'
        '/tmp/2019/03/27/*.tfrecords'
        '/tmp/2019/03/28/*.tfrecords'
    )

    test_pattern = ('/tmp/2019/03/29/*.tfrecords')

    train = Train()
    train.create_model()

    train.do_train(train_pattern, test_pattern)



#train.do_train(train_pattern, test_pattern)

#    train.do_train(('/bitlog/BALANCED/20190320/*.tfrecords', '/bitlog/BALANCED/20190321/*.tfrecords',
#                    '/bitlog/BALANCED/20190322/*.tfrecords', 
#                    '/bitlog/BALANCED/20190323/*.tfrecords',
#                    '/bitlog/BALANCED/20190325/*.tfrecords'), '/bitlog/2019/03/29/*.tfrecords')


#    train.do_train('gs://bitboard/2019/03/21/*.tfrecords', 'gs://bitboard/2019/03/22/*.tfrecords')



