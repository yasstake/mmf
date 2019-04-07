import glob
import sys
import os
import shutil
import random

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('python3 select_tffile.py org_dir copy_target_dir')


    dir = sys.argv[1]
    target_dir = sys.argv[2]

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

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for file in train_files:
        shutil.copy(file, target_dir)

