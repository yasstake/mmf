import sys
from log.dbloader import DbLoader

if __name__ == '__main__':
    log_dir = '/tmp'
    db_file = '/tmp/bitlog.db'

    if len(sys.argv) == 2:
        log_dir = sys.argv[0]
        db_file = sys.argv[1]

    print(log_dir, db_file)

    db_loader = DbLoader()
    db_loader.open_db()
    db_loader.load_dir(log_dir)
    db_loader.close_db()
