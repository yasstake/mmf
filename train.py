from dl.train import Train


train = Train()
train.create_model()

train.do_train('/tmp/2019/**/*.tfrecords')

