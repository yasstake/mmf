import numpy as np
import matplotlib.pyplot as plt

from log.dbgen import Generator


def show():
    g = Generator()
    gen1 = g.create(db_name='/bitlog/bitlog.db')

    board = next(gen1)
    board = next(gen1)

    mat = board.get_std_boards()[0]
    plt.figure()
    plt.imshow(mat, interpolation='nearest', vmin=0, vmax=255, cmap='jet')
    plt.show()

    mat = board.get_std_boards()[1]
    plt.figure()
    plt.imshow(mat, interpolation='nearest', vmin=0, vmax=255, cmap='jet')
    plt.show()

    mat = board.get_std_boards()[2]
    plt.figure()
    plt.imshow(mat, interpolation='nearest', vmin=0, vmax=255, cmap='jet')
    plt.show()

    mat = board.get_std_boards()[3]
    plt.figure()
    plt.imshow(mat, interpolation='nearest', vmin=0, vmax=255, cmap='jet')
    plt.show()


if __name__ == "__main__":
    show()

