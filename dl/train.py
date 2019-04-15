
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from dl.tfrecords import calc_class_weight
from dl.tfrecords import read_one_tf_file
from dl.tfrecords import read_tfrecord
from log import constant


class Train:
    def __init__(self):
        self.model = None
        self.config = None
        pass

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
        dataset = dataset.shuffle(buffer_size=100000)
        dataset = dataset.batch(50000)


        return dataset

    def test_data_set(self, file_pattern):
        print(file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        dataset = dataset.cache()
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(5000)


        return dataset

    def set_using_gpu(self):
        self.config = tf.ConfigProto(
            gpu_options=tf.GPUOptions(
                visible_device_list="0",  # specify GPU number
                allow_growth=True
            )
        )

    def do_train(self, train_pattern, test_pattern, calc_weight=True):
        weight = None
        if calc_weight:
            weight = calc_class_weight(train_pattern)
            print('weight->', weight)

        train_dataset = self.train_data_set(train_pattern)
        test_dataset  = self.test_data_set(test_pattern)

        print("start training loop ")

        for data in train_dataset:
            boards, ba, time = data

            boards = tf.io.decode_raw(boards, tf.uint8)
            boards = tf.reshape(boards, [-1, constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH])

            if weight:
                self.model.fit(boards, ba, batch_size=512, class_weight=weight, verbose=2)
            else:
                self.model.fit(boards, ba, batch_size=4096, verbose=2)

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

            score, precision, recall = self.predict_summary(ba, result)

            print('predict summary--->')
            print(score)

            print('precision--->')
            print(precision)

            print('recall--->')
            print(recall)


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
        precision = precision_score(p, a)
        recall = recall_score(p, a)

        return score, precision, recall

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

