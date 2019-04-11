import sys
from log.commands import *

if __name__ == '__main__':
    '''
    python3.7 blob2db.py yyyy mm dd [basename: default is gs:/xxx]

    year  = 0
    month = 12
    day   = 31
'''
    if len(sys.argv) < 4:
        print('blob2export.py yyyy mm dd [base]')
        exit(1)

    year  = int(sys.argv[1])
    month = int(sys.argv[2])
    day   = int(sys.argv[3])

    if len(sys.argv) == 4:
        base = '/tmp'
    elif len(sys.argv) == 5:
        base = sys.argv[4]
    else:
        base = 'gs://bitboard'

    print('export->', year, month, day, base)

    log2db(year, month, day)
    update_db(year, month, day)
    db2blob(year, month, day, base)

