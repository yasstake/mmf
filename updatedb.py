from log.logdb import LogDb
import os
import sys

if __name__ == "__main__":

    db_file = os.sep + 'tmp' + os.sep + 'bitlog.db'

    if len(sys.argv) == 2:
        db_file = sys.argv[1]

    print(db_file)

    db = LogDb(db_file)

    db.connect()
    db.create_cursor()
    db.update_all_order_prices(True)
    db.update_all_best_action(True)
    print(db.action_stat())
    db.close()
