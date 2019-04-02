from matplotlib import pyplot as plt
import numpy as np

class Plot:
    @staticmethod
    def show(array3d):
        #        array3d = np.stack(array4d[0], array4d[1], array4d[2], array[3])

        #array2d = np.stack(array4d[0], array4d[1], array4d[2])

        print(array3d.shape)
        print(array3d[0].shape)

        #        array2d = np.add(array3d[0],array3d[1])
        array2d = np.ndarray((100,100))

        plt.imshow(array2d, vmin=0, vmax=100)
        plt.figure()



if __name__ == "__main__":
    array = np.ndarray((4, 100, 100))

    Plot.show(array)

