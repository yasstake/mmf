import glob
import sys

from log.logdb import LogDb
from log.price import PriceBoardDB

'''
usage

python3.7 db2tfrecords.py [dbname] [outdir]
'''

if __name__ == '__main__':

    db_file = '/tmp/bitlog.db'
    export_dir = '/tmp'

    if len(sys.argv) <= 1:
        pass
    elif 2 <= len(sys.argv):
        db_files = glob.glob(sys.argv[1])

        if len(sys.argv) == 3:
            export_dir = sys.argv[2]

    skip = False

    for db_file in db_files:
        print(db_file, export_dir)

        db = LogDb(db_file)
        db.connect()
        db.create_cursor()

        db.update_all_order_prices(False)
        db.update_all_best_action(False)

        if skip:
            skip_number = db.skip_nop_close_to_action()
            print('skip rec->', skip_number)

        db.close()

        db = LogDb()
        db.connect()
        db.create_cursor()

        db.import_db(db_file)

        PriceBoardDB.export_board_to_blob(db_object=db, root_dir=export_dir)

        db.close()
