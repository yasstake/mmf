from dl.train import Train


if __name__ == "__main__":

    train = Train()
    train.create_model()

    train.do_train('/tmp/2019/03/17/*.tfrecords', '/tmp/2019/03/18/*.tfrecords')


