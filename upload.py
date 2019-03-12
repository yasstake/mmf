import os, sys, subprocess, glob


if __name__ == "__main__":
    log_dir = os.sep + 'tmp'

    if len(sys.argv) == 2:
        log_dir = sys.argv[1]

    file_list = glob.glob(log_dir + '/*.log.gz')

    print(file_list)




