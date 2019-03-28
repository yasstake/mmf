import sys
import os
from  log.price import PriceBoardDB
from log.dbloader import DbLoader

if __name__ == '__main__':
    log_db_name = '/tmp/bitlog.db'

    if 2  <= len(sys.argv):
        log_db_name = sys.argv[1]

    PriceBoardDB.export_board_to_blob(log_db_name)

