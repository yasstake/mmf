import sys
import os
from  log.price import PriceBoardDB
from log.dbloader import DbLoader
from log.logdb import LogDb

if __name__ == '__main__':

    db_file = '/tmp/bitlog.db'
    export_dir = '/tmp'

    if len(sys.argv) <= 1:
        pass
    elif len(sys.argv) <= 2:
        db_file = sys.argv[1]
        if len(sys.argv) <= 3:
            export_dir = sys.argv[2]

    print(db_file, export_dir)

    db = LogDb()
    db.connect()
    db.create_cursor()

    db.import_db(db_file)

    PriceBoardDB.export_board_to_blob(db_object=db)

