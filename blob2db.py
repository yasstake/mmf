import sys
import os
from log.dbloader import DbLoader
from log.logdb import LogDb

if __name__ == '__main__':
    '''
    python3.7 blob2db.py yyyy mm dd [db_file_name]

    db_file = os.sep + 'tmp' + os.sep + 'bitlog.db'
    blob_path = None
    year  = 0
    month = 12
    day   = 31
'''
    if 4 <= len(sys.argv):
        year  = int(sys.argv[1])
        month = int(sys.argv[2])
        day   = int(sys.argv[3])
    if len(sys.argv) == 5:
        db_file = sys.argv[4]

    print(year, month, day, db_file)

    db_loader = DbLoader()
    db_loader.open_db(db_file)
    db_loader.load_from_blob_by_date(year, month, day)
    db_loader.close_db()

    db = LogDb(db_file)
    db.connect()
    db.create_cursor()
    db.update_all_order_prices(True)
    db.commit()

