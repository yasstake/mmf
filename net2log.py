import os
import sys
from time import sleep

from log.bitws import BitWs

if __name__ == "__main__":
    log_dir   = os.sep + 'tmp'
    flag_file = os.sep + 'tmp' + os.sep + 'BITWS-FLG'
    pid = str(os.getpid())
    sleep_time = 3600   #1H

    print(len(sys.argv))

    if 3 <= len(sys.argv):
        log_dir = sys.argv[1]
        flag_file = sys.argv[2]

    if 4 == len(sys.argv):
        pid = sys.argv[3]

    print("net2log", log_dir, flag_file, pid)

    bitmex = BitWs(log_dir, flag_file, pid)
    bitmex.start()

    if bitmex.terminated_by_peer:
        print("terminated by peer : sleep->", sleep_time)
        sleep(sleep_time)
        print("sleep end")
