import os
import sys

from log.bitws import BitWs

if __name__ == "__main__":
    log_dir   = os.sep + 'tmp'
    flag_file = os.sep + 'tmp' + os.sep + 'BITWS-FLG'
    pid = str(os.getpid())

    print(len(sys.argv))

    if 3 <= len(sys.argv):
        log_dir = sys.argv[1]
        flag_file = sys.argv[2]

    if 4 == len(sys.argv):
        pid = sys.argv[3]

    print("logging_container", log_dir, flag_file, pid)

    bitmex = BitWs(log_dir, flag_file, pid)
    bitmex.start()

    if bitmex.terminated_by_peer:
        print("---terminated by peer------")
        sys.exit(0)

    sys.exit(-1)
