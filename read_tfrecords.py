import sys
import dl.tfrecords

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('python3.7 dl.tfrecords.py [readfile]')

    tffile = sys.argv[1]

    weight = dl.tfrecords.calc_class_weight(tffile)

    print('weigth->', weight)

    dl.tfrecords.read_one_tf_file(tffile)

