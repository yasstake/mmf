import glob
import sys
import os
import shutil
import random

if __name__ == '__main__':

    dir = './'

    if len(sys.argv) == 2:
        dir = sys.argv[1]

    number_of_files = [0,0,0,0,0]
    for i in range(0, 5):
        files = glob.glob(dir + '*.{:02d}.tfrecords'.format(i))

        for file in files:
            number_of_files[i] += 1

        print('[FILE]', i, 'number=', number_of_files[i])

    print(number_of_files)
    min_cluster = min(number_of_files)

    print(min_cluster)


    train_files = []
    for i in range(0, 5):
        files = glob.glob(dir + '*.{:02d}.tfrecords'.format(i))

        random.shuffle(files)
        files = files[:min_cluster]
        train_files += files
        random.shuffle(train_files)



    print(train_files)

    for file in train_files:
        shutil.copy(file, '/tmp/TRAIN/')

