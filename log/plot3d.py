from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from log.constant import TIME_WIDTH
from log.constant import BOARD_WIDTH
from log.dbgen import Generator

def show():
    g = Generator()
    gen1 = g.create(db_name='/bitlog/bitlog.db')

    board = next(gen1)
    x = np.arange(- int(BOARD_WIDTH / 2), (BOARD_WIDTH / 2), 1)
    y = np.arange(0, TIME_WIDTH, 1)

    X, Y = np.meshgrid(x, y)

    print(X.shape)

    print(Y.shape)

    mat = board.get_std_boards()[0]

    print(mat.shape)

    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_wireframe(X, Y, mat)  # <---ここでplot

    plt.show()



if __name__ == "__main__":
    show()



