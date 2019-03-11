import os
import sys
from log.bitws import BitWs

if __name__ == "__main__":
    log_dir   = os.sep + 'tmp'
    flag_file = os.sep + 'tmp' + os.sep + 'BITWS-FLG'

    if len(sys.argv) == 2:
        log_dir = sys.argv[0]
        flag_file = sys.argv[1]

    bitmex = BitWs(log_dir, flag_file)
    bitmex.start()
