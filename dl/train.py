
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix

from dl.tfrecords import calc_class_weight
from dl.tfrecords import read_one_tf_file
from dl.tfrecords import read_tfrecord
from log import constant

tf.enable_v2_behavior()

STEPS_PER_EPOC = 32



class Train:
    def __init__(self):
        self.model = None
        self.config = None
        self.train_dataset = None
        self.evaluate_dataset = None
        self.ba = None

    @staticmethod
    def loss_function(y_true, y_pred):
        pass

    def create_model(self):
        self.model = tf.keras.models.Sequential()

        self.model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH), padding='same'))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Flatten())
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Dropout(0.4))
        self.model.add(tf.keras.layers.Dense(units=5, activation='softmax'))

        self.model.summary()

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


    def train_data_set(self, file_pattern):
        print('train', file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset.cache()
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(10)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(STEPS_PER_EPOC)

        return dataset

    def test_data_set(self, file_pattern):
        print(file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset = dataset.cache()
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(1024)

        return dataset

    def set_using_gpu(self):
        self.config = tf.ConfigProto(
            gpu_options=tf.GPUOptions(
                visible_device_list="0",  # specify GPU number
                allow_growth=True
            )
        )


    def train_data_generator(self):
        for data in self.train_dataset:
            boards, ba, time = data

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards,
                                [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            yield (boards, ba)


    def train_data_generator(self):
        for data in self.train_dataset:
            boards, ba, time = data

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards,
                                [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            yield (boards, ba)


    def evaluate_data_generator(self):
        for data in self.evaluate_dataset:
            boards, ba, time = data

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards,
                                [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            print('dataset', boards.shape, time[0])

            self.ba = ba
            yield (boards, ba)



    def do_train(self, train_pattern, test_pattern, calc_weight=True):
        weight = None
        if calc_weight:
            weight = calc_class_weight(train_pattern)
            print('weight->', weight)

        train_dataset = self.train_data_set(train_pattern)
        test_dataset  = self.test_data_set(test_pattern)

        print("start training loop ")

        self.train_dataset = train_dataset

        self.evaluate_dataset = test_dataset
        self.model.fit_generator(generator=self.train_data_generator(), steps_per_epoch=STEPS_PER_EPOC, class_weight=weight, verbose=1)

        path = '/tmp/bitmodel.h5'
        self.model.save(path)

        result = self.model.predict_generator(generator=self.evaluate_data_generator(), steps=STEPS_PER_EPOC, verbose=1)

        score = self.predict_summary(self.ba, result)

        print('predict summary--->')
        print(score)


    def do_train2(self, train_pattern, test_pattern, calc_weight=True):
        weight = None
        if calc_weight:
            weight = calc_class_weight(train_pattern)
            print('weight->', weight)

        train_dataset = self.train_data_set(train_pattern)
        test_dataset  = self.test_data_set(test_pattern)

        print("start training loop ")

        for data in train_dataset:
            boards, ba, time = data

            print(boards.shape)

            boards = tf.io.decode_raw(boards, tf.uint8)

            print(boards.shape)

            boards = tf.reshape(boards, [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            print(boards.shape)

            if weight:
                self.model.fit(boards, ba, batch_size=2, class_weight=weight, verbose=1)
            else:
                self.model.fit(boards, ba, batch_size=4096, verbose=1)

        path = '/tmp/bitmodel.h5'
        self.model.save(path)

        for data in test_dataset:
            boards, ba, time = data

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards, [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            loss, acc = self.model.evaluate(boards, ba)
            print('evaluation->', loss, acc)
            #predict
            boards, ba, time = read_one_tf_file(test_pattern)

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards, [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            result = self.predict(boards)

            score = self.predict_summary(ba, result)

            print('predict summary--->')
            print(score)



    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)

    def predict(self, board):

        result = self.model.predict_proba((board))

        return result

    def predict_summary(self, answer, predict):
        p = []
        a = []
        for i in range(0, len(answer)):
            p.append(np.argmax(predict[i]))
            a.append(np.argmax(answer[i]))

        score = confusion_matrix(p, a)
        #precision = precision_score(p, a)
        #recall = recall_score(p, a)

        return score

    def print_predict_summary(self, score):
        shape = score.shape

        print(shape)

        print(score)


if __name__ == "__main__":


    train_pattern = (
        'gs://bitboard/2019/03/22/*.tfrecords',
        'gs://bitboard/2019/03/23/*.tfrecords',
        'gs://bitboard/2019/03/24/*.tfrecords',
        'gs://bitboard/2019/03/25/*.tfrecords',
        'gs://bitboard/2019/03/26/*.tfrecords',
        'gs://bitboard/2019/03/27/*.tfrecords',
        'gs://bitboard/2019/03/28/*.tfrecords',
        'gs://bitboard/2019/03/29/*.tfrecords',
        'gs://bitboard/2019/03/30/*.tfrecords',
        'gs://bitboard/2019/03/31/*.tfrecords'
    )

    test_pattern = ('gs://bitboard/2019/04/01/*.tfrecords')

    train_pattern = (
        '/bitlog/2019/03/23/*.tfrecords')
    
    train_pattern = (
        '/bitlog/2019/03/23/*.tfrecords',
        '/bitlog/2019/03/24/*.tfrecords',
        '/bitlog/2019/03/25/*.tfrecords',
        '/bitlog/2019/03/26/*.tfrecords',
        '/bitlog/2019/03/27/*.tfrecords',
        '/bitlog/2019/03/28/*.tfrecords',
        '/bitlog/2019/03/29/*.tfrecords',
        '/bitlog/2019/03/30/*.tfrecords',
        '/bitlog/2019/03/31/*.tfrecords',
        '/bitlog/2019/04/01/*.tfrecords',
        '/bitlog/2019/04/02/*.tfrecords',
        '/bitlog/2019/04/03/*.tfrecords',
        '/bitlog/2019/04/04/*.tfrecords',
        '/bitlog/2019/04/05/*.tfrecords',
        '/bitlog/2019/04/06/*.tfrecords'
    )


    test_pattern = ('/bitlog/2019/04/07/*.tfrecords')


    train_pattern = (
        '/tmp/2019/03/22/*.tfrecords'
    )

    test_pattern = ('/tmp/2019/03/22/*.tfrecords')

    train = Train()
    train.create_model()

    train.do_train(train_pattern, test_pattern)

