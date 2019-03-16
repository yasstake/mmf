import sys
import os
from log.dbloader import DbLoader

if __name__ == '__main__':
    '''
    python3.7 blob2db.py blob_path [db_file_name]
    '''
    db_file = os.sep + 'tmp' + os.sep + 'bitlog.db'
    blob_path = None

    if len(sys.argv) <= 2:
        blob_path = sys.argv[1]
    if len(sys.argv) == 3:
        db_file = sys.argv[2]

    print(blob_path, db_file)

    db_loader = DbLoader()
    db_loader.open_db()
    db_loader.load_from_blobs(blob_path)
    db_loader.close_db()
