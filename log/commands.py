import os
from log.dbloader import DbLoader
from log.price import PriceBoardDB
from log.logdb import LogDb
from log.timeutil import time_sec


def logdir2db(path, db_file):
    db_loader = DbLoader()
    db_loader.open_db(db_file=db_file)
    db_loader.load_dir(path)
    db_loader.close_db()


def log2db(year, month, day):
    db_file = '/tmp/{:04d}-{:02d}-{:02d}.db'.format(year, month, day)

    # load blob2db
    db_loader = DbLoader()
    db_loader.open_db(db_file=db_file)
    db_loader.load_from_blob_by_date(year, month, day)
    db_loader.close_db()


def update_db(year, month, day):
    db_file = '/tmp/{:04d}-{:02d}-{:02d}.db'.format(year, month, day)
    # updae db
    db = LogDb(db_file)

    db.connect()
    db.create_cursor()
    db.update_all_order_prices()
    db.update_all_best_action()
    #db.skip_nop_close_to_action()
    db.close()


def db2blob(year, month, day, root_dir):
    db_file = '/tmp/{:04d}-{:02d}-{:02d}.db'.format(year, month, day)

    db = LogDb()
    db.connect()
    db.create_cursor()

    db.import_db(db_file)

    date = '{:04d}-{:02d}-{:02d}'.format(year, month, day)

    start_time = int(time_sec(date + 'T00:00:00.00'))
    end_time = start_time + 24 * 60 * 60

    PriceBoardDB.export_board_to_blob(db_object=db, start_time=start_time, end_time=end_time, root_dir=root_dir)

    db.close()

