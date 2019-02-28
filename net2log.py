import atexit
from log.bitws import BitWs

if __name__ == "__main__":
    bitmex = BitWs(log_file_dir="")
    bitmex.start()
