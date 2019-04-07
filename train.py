from dl.train import Train


if __name__ == "__main__":

    train = Train()
    train.create_model()
#    train.do_train('/tmp/2019/T/*.tfrecords', '/tmp/2019/T/*.tfrecords')
    train.do_train('/tmp/TRAIN/*.tfrecords', '/tmp/2019/03/21/*.tfrecords')

#    train.do_train(('/tmp/2019/03/17/*.tfrecords', '/tmp/2019/03/18/*.tfrecords',
#                    '/tmp/2019/03/19/*.tfrecords', '/tmp/2019/03/20/*.tfrecords'),
#                   '/tmp/2019/03/21/*.tfrecords')


#    train.do_train('gs://bitboard/2019/03/21/*.tfrecords', 'gs://bitboard/2019/03/22/*.tfrecords')




