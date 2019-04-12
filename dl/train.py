
import numpy as np
import tensorflow as tf
# import tensorflow.python.keras as keras
import tensorflow.contrib.keras.api.keras as keras
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from dl.tfrecords import calc_class_weight
from dl.tfrecords import decode_buffer
from dl.tfrecords import read_one_tf_file
from dl.tfrecords import read_tfrecord
from log import constant


class Train:
    def __init__(self):
        self.model = None
        pass

    @staticmethod
    def loss_function(y_true, y_pred):
        pass
        #return keras.K.mean(K.abs(y_pred - y_true))

    def create_model(self):
        self.model = keras.models.Sequential()

        self.model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(constant.NUMBER_OF_LAYERS, constant.BOARD_TIME_WIDTH, constant.BOARD_WIDTH), padding='same'))
        self.model.add(keras.layers.BatchNormalization())
        self.model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        self.model.add(keras.layers.BatchNormalization())
        self.model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
        self.model.add(keras.layers.BatchNormalization())
        self.model.add(keras.layers.Flatten())
        self.model.add(keras.layers.BatchNormalization())        
        self.model.add(keras.layers.Dropout(0.4))
        self.model.add(keras.layers.Dense(units=5, activation='softmax'))

        self.model.summary()

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


    def train_data_set(self, file_pattern):
        print('train', file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        #dataset.cache('/tmp/data.cache')
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(5000)

        return dataset

    def test_data_set(self, file_pattern):
        print(file_pattern)

        input_dataset = tf.data.Dataset.list_files(file_pattern)
        dataset = tf.data.TFRecordDataset(input_dataset, compression_type='GZIP')
        #dataset = dataset.cache("./tfcache")
        dataset = dataset.map(read_tfrecord)
        dataset = dataset.repeat(1)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.batch(5000)

        return dataset


    def do_train(self, train_pattern, test_pattern):
        weight = calc_class_weight(train_pattern)

        print('weight->', weight)

        train_dataset = self.train_data_set(train_pattern)
        test_dataset  = self.test_data_set(test_pattern)

        train_iterator = train_dataset.make_initializable_iterator()
        train_next_dataset = train_iterator.get_next()

        test_iterator = test_dataset.make_one_shot_iterator()
        test_next_dataset = test_iterator.get_next()

        print("start session")

                
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(train_iterator.initializer)

            while True:
                try:
                    board_array, ba, time = sess.run(train_next_dataset)

                    boards = np.stack(list(map(decode_buffer, board_array)))

                    self.model.fit(boards, ba, batch_size=512, class_weight=weight, verbose=2)

                except tf.errors.OutOfRangeError as e:
                    print('training end')
                    break
                    pass

            path = '/tmp/bitmodel.h5'
            self.model.save(path)

            # Evaluate
            try:
                board_array, ba, time = sess.run(test_next_dataset)
                boards = np.stack(list(map(decode_buffer, board_array)))

                loss, acc = self.model.evaluate(boards, ba)
                print('evaluation->', loss, acc)

            except tf.errors.OutOfRangeError as e:
                pass

            #predict
            boards, ba, time = read_one_tf_file(test_pattern)

            result = self.predict(boards)

            score, precision, recall = self.predict_summary(ba, result)

            print('predict summary--->')
            print(score)

            print('precision--->')
            print(precision)

            print('recall--->')
            print(recall)


    def load_model(self, path):
        self.model = keras.models.load_model(path)

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
    
    train = Train()
    train.create_model()

    train.do_train(train_pattern, test_pattern)



