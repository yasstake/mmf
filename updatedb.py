from log.logdb import LogDb
import os
import sys

if __name__ == "__main__":
    log_dir = os.sep + 'tmp'
    db_file = os.sep + 'tmp' + os.sep + 'bitlog.db'

    if len(sys.argv) == 3:
        log_dir = sys.argv[1]
        db_file = sys.argv[2]

    print(log_dir, db_file)

    db = LogDb(db_file)

    db.connect()
    db.update_all_order_prices()
    db.close()
