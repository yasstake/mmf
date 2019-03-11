import os
import sys
from log.bitws import BitWs

if __name__ == "__main__":
    log_dir   = os.sep + 'tmp'
    flag_file = os.sep + 'tmp' + os.sep + 'BITWS-FLG'

    print(len(sys.argv))

    if len(sys.argv) == 3:
        log_dir = sys.argv[1]
        flag_file = sys.argv[2]

    print("net2log", log_dir, flag_file)

    bitmex = BitWs(log_dir, flag_file)
    bitmex.start()
